#
# Copyright (c) 2005-2007, Scientific Computing Associates, Inc.
#
# NetWorkSpaces is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307
# USA
#

# server for NetWorkSpaces.

import os, mmap, traceback

from tempfile import mkstemp
from random import randint

from twisted.application import internet, service
from twisted.internet import defer, protocol, reactor
from twisted.python import log
from twisted.web import server

from nwss.protocol import NwsProtocol
from nwss.web import NwsWeb

from nwss.babelConfig import *
from nwss.dummyComm import *
from nwss.hexDump import hexDump

import nwss.config

# bit codings for the descriptor.
DirectString = 1
_DEBUG = 0

class netWorkSpace:
    def __init__(self, name, owned=False, owner='', persistent=False):
        self.bindings = {}  # maps from a variable name to a Variable object
        self.name = name
        self.owned = owned
        self.owner = owner
        self.persistent = persistent

class Variable:
    def __init__(self, wsName, varName, mode='unknown'):
        self._wsName = wsName
        self._varName = varName
        self.fetchers, self.finders, self.values = [], [], []
        self.mode = mode
        self._errorValue = Value(0, '')
        self._id = '%020u' % randint(0, 999999999)
        self._index = 0

    def getName(self):
        return "%s @ %s" % (self._wsName, self._varName)

    def purge(self):
        for c in self.fetchers: c.writeStatusLenValue((1, '', 0, self._errorValue))
        for c in self.finders: c.writeStatusLenValue((1, '', 0, self._errorValue))
        for val in self.values: val.close()
        self.fetchers, self.finders, self.values = [], [], []

    def format(self, name):
        return '%s\t%d\t%d\t%d\t%s' % (name, len(self.values),
                len(self.fetchers), len(self.finders), self.mode)

    def setVar(self, cState, val, varId=''):
        if varId.strip() and varId != self._id:
            if _DEBUG: log.msg('variable id mismatch')
            cState.writeStatus('0001')
            if _DEBUG: log.msg('setVar finished')
            return

        valIndex = self._index + len(self.values)

        # give the value to all finders that are waiting for a value
        for c in self.finders:
            if _DEBUG: log.msg('calling a finder back')
            c.writeStatusLenValue((0, self._id, valIndex, val))
            if _DEBUG: log.msg('returning from finder writeStatusLenValue')

        self.finders = []

        # give it to a fetcher, or save it if no one is waiting
        if self.fetchers:
            if _DEBUG: log.msg('calling a fetcher back')
            c = self.fetchers.pop(0)
            c.writeStatusLenValue((0, self._id, valIndex, val))
            self._index += 1
            if _DEBUG: log.msg('returning from fetcher writeStatusLenValue')
        elif 'single' == self.mode:
            if self.values:
                self.values[0].close() # might be a long value
                self.values[0] = val
            else:
                self.values.append(val)
        else:
            self.values.append(val)

        if _DEBUG: log.msg('writing status to client')
        cState.writeStatus('0000')
        if _DEBUG: log.msg('setVar finished')

    def getVar(self, cState, removeP, blockP, iterateP, varId='', valIndex=0):
        n = len(self.values)

        if iterateP:
            # XXX note that if n == 0, the variable's mode could still be unknown.
            # XXX in that case, the first value will always be given to the iterator,
            # XXX even if the mode has since been set to lifo or multi.
            if self.mode in ['lifo', 'multi']:
                if _DEBUG: log.msg('iterated operation attempted on variable with mode: ' + self.mode)
                # XXX what's the correct error handling for this case?
                cState.writeStatusLenValue((1, '', 0, self._errorValue))
                return

            if varId.strip():
                if varId != self._id:
                    if _DEBUG: log.msg('variable id mismatch')
                    # XXX what's the correct error handling for this case?
                    cState.writeStatusLenValue((1, '', 0, self._errorValue))
                    return

                # don't allow index to go negative if someone has fetched your next value
                x = max(valIndex - self._index + 1, 0)
                success = x < n
            else:
                x = 0
                success = n > 0
        else:
            success = n > 0
            if success:
                # if we have values for this Variable, the mode cannot be 'unknown'.
                if self.mode == 'single':   x = 0
                elif self.mode == 'lifo':   x = n - 1
                elif self.mode == 'fifo':   x = 0
                elif self.mode == 'multi':  x = randint(0, n - 1)
                else: raise AssertionError, 'variable has illegal mode: ' + self.mode

        if success:
            if removeP:
                if _DEBUG: log.msg('returning fetched value')
                val = self.values.pop(x)
                val.consumed()  # needed in case it's a long value
            else:
                if _DEBUG: log.msg('returning found value')
                val = self.values[x]

            cState.varId = self._id
            valIndex = self._index + x
            cState.writeStatusLenValue((0, self._id, valIndex, val))
            if removeP: self._index += 1
        else:
            if blockP:
                if removeP:
                    if _DEBUG: log.msg('queueing up blocking fetch request')
                    self.fetchers.append(cState)
                    cState.blockingList = self.fetchers
                else:
                    if _DEBUG: log.msg('queueing up blocking find request')
                    self.finders.append(cState)
                    cState.blockingList = self.finders

                cState.blockingVar = self
            else:
                if _DEBUG: log.msg('returning unsuccessful reply')
                cState.writeStatusLenValue((1, '', 0, self._errorValue))

class ValueTranslation:
    def __init__(self, server, value, cb, *a):
        self.dc = DummyConnection(self.writeStatusLenValue)
        self.d = defer.Deferred()
        self.d.addCallback(cb, *a)
        envId = (value.desc() >> 24) & 0xFF

        try:
            babelNwsName, self.tcb = babelEngines[envId]
            status = server.openWs(self.dc, 'use ws', babelNwsName, '',
                    'no', 'no')

            if status == 0:
                server.setVar(self.dc, 'store', babelNwsName, 'food',
                        value.desc(), value.val())
                server.getVar(self.dc, 'fetch', babelNwsName, 'doof')
            else:
                self.d.callback('[error: %s not running]' % babelNwsName)
        except KeyError:
            self.d.callback('[error: unknown babel engine]')

    def writeStatusLenValue(self, (status, varId, valIndex, value)):
        # XXX can safely ignore varId and valIndex?
        self.tcb(self.d, value.val())

class Value:
    def __init__(self, desc, val):
        self._desc = desc
        self._val = val
        self._consumed = False

        if isinstance(val, str):
            self._long = False
            self._length = len(val)
        else:
            # if it's not a string, assume it's a tuple: (filename, length)
            self._long = True
            self._length = val[1]

    # called from getVar when the operation consumes the value
    def consumed(self):
        self._consumed = True

    # called from protocol after the value is sent to the client
    def accessComplete(self):
        if self._consumed: self.close()

    # this actually deletes the file, if there is a file
    def close(self):
        if self._long:
            try:
                os.remove(self._val[0])
            except:
                e = sys.exc_info()[1]
                log.msg('error removing file %s: %s' % (self._val[0], str(e)))

    def getFile(self):
        assert self._long, 'getFile illegally called on string value'
        f = open(self._val[0], 'rb')
        m = mmap.mmap(f.fileno(), self._length, access=mmap.ACCESS_READ)
        f.close()
        return m

    def isLarge(self):
        return self._long

    def desc(self):
        return self._desc

    def val(self):
        assert not self._long, 'val illegally called on long value'
        return self._val

    def length(self):
        return self._length

    def translate(self, server, cb, *a):
        if self._long:
            cb('<long value>', *a)
        elif self._desc & DirectString:
            cb(self._val, *a)
        else:
            ValueTranslation(server, self, cb, *a)

def varList(bindings):
    k = bindings.keys()
    k.sort()
    return ','.join(k)

class NwsService(internet.TCPServer):
    # marker for list output.
    myOwnDesignation = {True: '>', False: ' '}

    # tuples here encode the properties remove and block.
    lValueOps = { 'fetch':  (1, 1, 0), 'fetchTry':  (1, 0, 0), 'find':  (0, 1, 0), 'findTry':  (0, 0, 0),
                  'ifetch': (1, 1, 1), 'ifetchTry': (1, 0, 1), 'ifind': (0, 1, 1), 'ifindTry': (0, 0, 1) }

    # allowable queing modes for variables.
    modes = ['fifo', 'lifo', 'multi', 'single']

    nullValue = Value(0, '')

    def __init__(self, port, **kw):
        self._factory = NwsFactory(self)
        internet.TCPServer.__init__(self, port, self._factory, **kw)
        self.extToIntWsName = {'__default' : ('__default', 0)}
        self.spaces = {('__default', 0) : netWorkSpace('__default', True, '[system]')}

        self.opTable = {
            'declare var':      self.declareVar,
            'delete ws':        self.deleteNetWorkSpace,
            'delete var':       self.deleteVar,
            'fetch':            self.getVar,
            'ifetch':           self.getVar,
            'fetchTry':         self.getVar,
            'ifetchTry':        self.getVar,
            'find':             self.getVar,
            'ifind':            self.getVar,
            'findTry':          self.getVar,
            'ifindTry':         self.getVar,
            'list vars':        self.listVars,
            'list wss':         self.listWss,
            'mktemp ws':        self.mktempWs,
            'open ws':          self.openWs,
            'store':            self.setVar,
            'use ws':           self.openWs,
        }

        self.wsCounter = 0

    def startService(self):
        tmpdir = nwss.config.nwsTmpDir
        log.msg('using temp directory ' + tmpdir)
        fd, self.tmpFileName = mkstemp(prefix='__nwss', dir=tmpdir)
        self.wsBaseName = os.path.basename(self.tmpFileName)
        try: os.close(fd)
        except: pass

    def stopService(self):
        log.msg('stopping NwsService')
        try: os.remove(self.tmpFileName)
        except: pass

        # purge all netWorkSpace objects, which will remove the temp files
        # currently in use
        for k, v in self.spaces.items():
            try:
                self.purgeNetWorkSpace(v.bindings)
            except:
                e = sys.exc_info()[1]
                log.msg("caught exception while purging workspace %s: %s" % (k[0], str(e)))

        log.msg('stopping complete')

    def doOp(self, cState):
        # dispatch
        try:    self.opTable[cState.args[0]](cState, *cState.args)
        except  Exception, e:
            traceback.print_exc()
            log.msg('ignoring: '+ str(cState.args) + ' ' + str(e))

    def referenceSpace(self, wsName, cState, assertOwnership=False,
            owner='', willingToCreate=True):
        if not self.extToIntWsName.has_key(wsName):
            # return an error if the workspace shouldn't be created
            if not willingToCreate:
                return 1

            # don't recognize the external workspace name, create it. we use a
            # separate internal name that allows has to track instances. e.g.,
            # workspace 'foo' is created, deleted and created again. a
            # connection using the first may map 'foo' to the internal "name"
            # the tuple '(foo, 1)' while a connection using the second may map
            # 'foo' to '(foo, 7)'.

            intWsName = (wsName, self.wsCounter)
            self.wsCounter += 1
            if assertOwnership:
                self.spaces[intWsName] = netWorkSpace(wsName, True, owner)
                cState.mySets.append(intWsName)
            else:
                self.spaces[intWsName] = netWorkSpace(wsName)
            self.extToIntWsName[wsName] = intWsName
        else:
            intWsName = self.extToIntWsName[wsName]
            space = self.spaces[intWsName]
            if not space.owned and assertOwnership:
                space.owned, space.owner = True, owner
                cState.mySets.append(intWsName)

        if cState.wsMap.get(wsName, intWsName) != intWsName:
            if _DEBUG: log.msg('connection has new reference (%s, %s)' % (cState.wsMap[wsName], intWsName))
        cState.wsMap[wsName] = intWsName
        return 0

    def declareVar(self, cState, op, wsName, varName, mode):
        if _DEBUG: log.msg('declareVar called on behalf of ' + str(cState))
        try:    bindings = self.spaces[cState.wsMap[wsName]].bindings
        except:
            if _DEBUG: log.msg('has this connection opened/used %s?' % (wsName))
            # eventually return error via status bytes.
            cState.writeStatus('0000')
            return

        if mode not in self.modes:
            log.msg('variable "%s", binding set "%s": unrecognized mode "%s", using fifo.' % (varName, wsName, mode))
            mode = 'fifo'

        status = '0000'
        if bindings.has_key(varName):
            if bindings[varName].mode == 'unknown':
                bindings[varName].mode = mode
            elif bindings[varName].mode != mode:
                if _DEBUG:
                    log.msg('variable "%s" (mode %s) already exists in netWorkSpace ' \
                            '"%s" with a different mode (%s), ignoring declare.' % \
                            (varName, mode, wsName, bindings[varName].mode))
                status = '0001'
        else:
            bindings[varName] = Variable(wsName, varName, mode)

        cState.writeStatus(status)

    def deleteNetWorkSpace(self, cState, op, wsName):
        if _DEBUG: log.msg('deleteNetWorkSpace called on behalf of ' + str(cState))
        try:
            self.purgeNetWorkSpace(self.spaces.pop(self.extToIntWsName[wsName]).bindings)
            self.extToIntWsName.pop(wsName)
            cState.writeStatus('0000')
        except KeyError:
            if _DEBUG: log.msg('binding set %s does not exist.' % wsName)
            cState.writeStatus('0001')

    def deleteVar(self, cState, op, wsName, varName):
        if _DEBUG: log.msg('deleteVar called on behalf of ' + str(cState))
        try:    bindings = self.spaces[cState.wsMap[wsName]].bindings
        except:
            if _DEBUG: log.msg('has this connection opened/used %s?' % (wsName))
            cState.writeStatus('0001')
            return

        try:
            var = bindings.pop(varName)
        except KeyError:
            log.msg('cannot delete "%s" in binding set "%s".' % (varName, wsName))
            cState.writeStatus('0001')
        else:
            var.purge()
            cState.writeStatus('0000')

    def getVar(self, cState, op, wsName, varName, varId='', valIndex=0):
        if _DEBUG: log.msg('getVar (%s) called on behalf of %s' % (op, str(cState)))
        try:    bindings = self.spaces[cState.wsMap[wsName]].bindings
        except:
            if _DEBUG: log.msg('has this connection opened/used %s?' % (wsName))
            cState.writeStatusLenValue((1, '', 0, self.nullValue))
            return

        try:
            var = bindings[varName]
        except KeyError:
            var = bindings[varName] = Variable(wsName, varName)

        removeP, blockP, iterateP = self.lValueOps[op]
        var.getVar(cState, removeP, blockP, iterateP, varId, int(valIndex))

    def listVars(self, cState, op, wsName):
        if _DEBUG: log.msg('listVars called on behalf of ' + str(cState))
        try:    bindings = self.spaces[cState.wsMap[wsName]].bindings
        except:
            if _DEBUG: log.msg('has this connection opened/used %s?' % (wsName))
            cState.writeStatusLenValue((1, '', 0, self.nullValue))
            return

        vars = bindings.keys()
        vars.sort()
        varListData = '\n'.join([bindings[varName].format(varName) for varName in vars])
        cState.writeStatusLenValue((0, '', 0, Value(0, varListData)))

    def listWss(self, cState, op, wsName=None):
        if _DEBUG: log.msg('listWss called on behalf of ' + str(cState))
        wsNames = self.extToIntWsName.keys()
        wsNames.sort()
        setList = '\n'.join(['%s%s\t%s\t%s\t%d\t%s'%(self.myOwnDesignation[n in cState.mySets],
                                                     n[0],
                                                     self.spaces[n].owner,
                                                     self.spaces[n].persistent,
                                                     len(b),
                                                     varList(b))
                             for extName in wsNames if (not wsName or wsName == extName)
                             for n in [self.extToIntWsName[extName]]
                             for s in [self.spaces[n]]
                             for b in [s.bindings]]) + '\n'
        cState.writeStatusLenValue((0, '', 0, Value(0, setList)))

    def mktempWs(self, cState, op, template='__ws__%d'):
        if _DEBUG: log.msg('mktempWs called on behalf of ' + str(cState))
        # step the counter on every attempt.
        cc = self.wsCounter
        self.wsCounter += 1

        try:    newName = (template % cc) + self.wsBaseName
        except:
            if _DEBUG: log.msg('mktemp: bad template "%s".' % template)
            cState.writeStatusLenValue((1, '', 0, self.nullValue))
            return

        if self.extToIntWsName.has_key(newName):
            if _DEBUG: log.msg('mktemp: new name "%s" already exists!' % newName)
            cState.writeStatusLenValue((1, '', 0, self.nullValue))
            return

        # make a non-owning reference (triggering existence).
        self.referenceSpace(newName, cState)
        cState.writeStatusLenValue((0, '', 0, Value(0, newName)))

    def openWs(self, cState, op, wsName, ownerData, persistent, create='yes'):
        if _DEBUG: log.msg('openWs called on behalf of ' + str(cState))
        willingToCreate = True
        if create != 'yes':
            willingToCreate = False

        if op == 'open ws':
            ownerDataTxt = '%s (%s)' % (cState.peer, ownerData)
            status = self.referenceSpace(wsName, cState, True,
                    ownerDataTxt, willingToCreate)
            if status == 0 and 'yes' == persistent:
                self.spaces[cState.wsMap[wsName]].persistent = True
        else:
            status = self.referenceSpace(wsName, cState, False, '',
                    willingToCreate)

        cState.writeStatus(('%04d' % status)[-4:])
        return status

    def purgeNetWorkSpace(self, bindings):
        keys = bindings.keys()
        for k in keys:
            var = bindings.pop(k)
            var.purge()

    def purgeOwnedWorkspaces(self, cState):
        for intWsName in cState.mySets:
            extWsName = intWsName[0]
            try:
                if not self.spaces[intWsName].persistent:
                    space = self.spaces.pop(intWsName)
                    self.purgeNetWorkSpace(space.bindings)
                    self.extToIntWsName.pop(extWsName)
            except Exception, e:        log.msg('purging %s: %s' % (intWsName, str(e)))

    def setVar(self, cState, op, wsName, varName, valDesc, valPayload, varId=''):
        if _DEBUG: log.msg('setVar called on behalf of ' + str(cState))
        try:    bindings = self.spaces[cState.wsMap[wsName]].bindings
        except:
            if _DEBUG: log.msg('has this connection opened/used %s?' % (wsName))
            cState.writeStatus('0001')
            return

        if not bindings.has_key(varName):
            bindings[varName] = Variable(wsName, varName, 'fifo')
        else:
            if bindings[varName].mode == 'unknown':
                bindings[varName].mode = 'fifo'

        var = bindings[varName]
        val = Value(int(valDesc), valPayload)
        var.setVar(cState, val, varId)

    def getResource(self):
        return NwsWeb(self)

    # this method is called by the NwsProtocol object when
    # it loses it's connection
    def protocolLostConnection(self, cState):
        self.purgeOwnedWorkspaces(cState)
        self.cancelBlockingOperation(cState)
        try:
            del cState.factory._protocols[cState._protokey]
            if _DEBUG: log.msg("after removing protocol: " + str(cState.factory._protocols))
        except:
            e = sys.exc_info()[1]
            log.msg("warning: problem removing protocol from " \
                    "factory's dictionary: " + str(e))

    def cancelBlockingOperation(self, cState):
        if cState.blocking:
            for i in xrange(len(cState.blockingList)):
                c = cState.blockingList[i]

                # I believe this is a valid definition of equality
                if c.sessionno == cState.sessionno:
                    del cState.blockingList[i]
                    if _DEBUG: log.msg("removed client from blocking list")
                    break
            else:
                log.msg("WARNING: client is blocking, but not in the blocking list")
        else:
            if _DEBUG: log.msg("client was not blocking")

        # clean up, making sure that we're not referencing anyone
        cState.blocking = 0
        cState.blockingList = []
        cState.blockingVar = None

class NwsFactory(protocol.ServerFactory):
    def __init__(self, service):
        self.protocol = NwsProtocol
        self.doOp = service.doOp
        self.goodbye = service.protocolLostConnection

        # keep a list of the protocol objects that we've created
        self._protocols = {}
        self._protokey = 0

    def buildProtocol(self, addr):
        p = protocol.Factory.buildProtocol(self, addr)
        p._protokey = self._protokey
        self._protocols[p._protokey] = p
        self._protokey += 1
        if _DEBUG: log.msg('built a new protocol[%d]: %s' % (p._protokey, str(self._protocols)))
        return p
