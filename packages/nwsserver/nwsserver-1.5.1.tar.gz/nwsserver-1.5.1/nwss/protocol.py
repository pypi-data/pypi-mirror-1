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

import os, sys, time
from tempfile import mkstemp
from twisted.protocols import stateful
from twisted.python import log
import nwss.config

_MIN_LONG_VALUE_SIZE = 64
_BUFFER_SIZE = 16 * 1024
_DEBUG = 0

class NwsProtocol(stateful.StatefulProtocol):

    # generic protocol: first 4 bytes are 4 ascii digits holding a
    # count of the args. each arg is a 20 digit length followed by
    # that many bytes holding the 'value' of the arg.

    # why 20? 2^64 fits into 20 digits. The string
    # '99999999999999999999' is allowed for the count of args.  it
    # means keep reading args until another '99999999999999999999' is
    # encountered as the len of an arg.

    # XXX how can an arg count of '99999999999999999999' be allowed when
    # we only use 4 ascii digits? should I fix or disable this? (steve)

    # the operation itself is an argument, so there should always be
    # at least one arg.

    sentinelCount = '99999999999999999999'

    def __str__(self):
        if hasattr(self, 'peer'):
            return 'NwsProtocol[%s]' % self.peer
        else:
            return 'NwsProtocol[not connected]'

    def connectionMade(self):
        self.transport.setTcpNoDelay(1)
        self.transport.setTcpKeepAlive(1)

        # this is start state for argument processing. the initial
        # state for the connection is "handshake".
        self.startState = (self.receiveArgCount, 4)

        # per connection opaque state to be manipulated by the eval
        # service.
        self.peer = str(self.transport.getPeer())
        self.mySets = [] # tracks workspaces owned by this connection.
        self.wsMap = {}  # map from external to internal workspace name.  see server.

        # used only for monitoring/display purposes
        self.sessionno = self.transport.sessionno
        self.numOps = 0
        self.lastOp = ''
        self.lastOpTime = time.asctime()
        self.numLongValues = 0

        # these are used to cancel a blocking operation if we lose our connection
        self.blocking = 0
        self.blockingList = []  # either the fetchers or finders list in a Variable
        self.blockingVar = None  # the Variable that we're blocking for

        # used when an error occurs while handling incoming request
        self.errorValue = ErrorValue()

    def handshake(self, data):
        if _DEBUG: log.msg('handshake called with: ' + repr(data))

        # will eventually do some interesting protocol versioning
        # reconciliation and option processing here.
        self.context = data
        self.transport.write('2223')

        return self.startState

    def connectionLost(self, reason):
        if _DEBUG: log.msg('connectionLost called')
        self.factory.goodbye(self)

    def writeStatusLenValue(self, (status, varId, valIndex, value)):
        if _DEBUG: log.msg("writeStatusLenValue: status = %d; len = %d" % (status, value.length()))

        self.blocking = 0
        self.blockingList = []
        self.blockingVar = None

        if self.context not in ['0000', '1111']:
            # this client supports the badly named 'cookie' protocol
            self.transport.write('%04d%020d%-20.20s%020d%020d' % (status,
                    value.desc(), varId, valIndex, value.length()))
        else:
            self.transport.write('%04d%020d%020d' % (status,
                    value.desc(), value.length()))

        if value.isLarge():
            if _DEBUG: log.msg("using long value protocol")
            producer = FileProducer(value, _BUFFER_SIZE, self.transport)
            self.transport.registerProducer(producer, None)
        else:
            self.transport.write(value.val())

    def writeStatus(self, statusString):
        if _DEBUG: log.msg("writeStatus: status = %s" % statusString)

        assert len(statusString) == 4

        self.blocking = 0
        self.blockingList = []
        self.blockingVar = None

        self.transport.write(statusString)

    def getInitialState(self): return (self.handshake, 4)

    def receiveArgCount(self, data):
        if _DEBUG: log.msg('receiveArgCount called with: ' + repr(data))

        if self.blocking:
            log.msg('error: received request while connection was busy')
            self.transport.loseConnection()
            return self.startState

        if data == self.sentinelCount:
            self.argCount = -1
        else:
            try:
                self.argCount = int(data)
            except ValueError:
                log.msg("error: got bad data from client")
                self.transport.loseConnection()
                return self.startState

            if self.argCount < 1:
                log.msg('error: bad arg count: ' + data)
                self.transport.loseConnection()
                return self.startState

        self.args = []
        self.errorOccurred = False
        return (self.receiveLenArg, 20)

    def receiveLenArg(self, data):
        if _DEBUG: log.msg('receiveLenArg called with: ' + repr(data))

        if self.argCount == -1 and data == self.sentinelCount:
            if self.errorOccurred:
                # XXX theoretically may need to call writeStatusLenValue
                self.writeStatus("0001")
            else:
                self.blocking = 1
                self.factory.doOp(self)
                self.numOps += 1
                self.lastOp = self.args[0]
                self.lastOpTime = time.asctime()
            return self.startState
        else:
            try:
                dlen = int(data)
            except ValueError:
                log.msg("error: got bad data from client")
                self.transport.loseConnection()
                return self.startState

            if dlen >= max(_MIN_LONG_VALUE_SIZE, nwss.config.nwsLongValueSize):
                if _DEBUG: log.msg('long value')
                self.bigArgLen = self.arglen = dlen
                self.lenRequested = min(_BUFFER_SIZE, dlen)
                self.numLongValues += 1

                try:
                    fd, self.tmpname = mkstemp(prefix='__nwss',
                            suffix='.dat', dir=nwss.config.nwsTmpDir)
                    self.tmpfile = os.fdopen(fd, 'w+b')
                except:
                    e = sys.exc_info()[1]
                    log.msg('error creating temporary file: ' + str(e))
                    self.errorOccurred = True

                return (self.receiveBigArg, self.lenRequested)
            else:
                return (self.receiveArg, dlen)

    def receiveArg(self, data):
        if _DEBUG: log.msg('receiveArg called')

        if not self.errorOccurred: self.args.append(data)

        if len(self.args) == self.argCount:
            if self.errorOccurred:
                # XXX theoretically may need to call writeStatusLenValue
                self.writeStatus("0001")
            else:
                self.blocking = 1
                self.factory.doOp(self)
                self.numOps += 1
                self.lastOp = self.args[0]
                self.lastOpTime = time.asctime()
            return self.startState
        else:
            return (self.receiveLenArg, 20)

    def receiveBigArg(self, data):
        if _DEBUG: log.msg('receiveBigArg called')

        if not self.errorOccurred: self.tmpfile.write(data)

        self.bigArgLen -= self.lenRequested
        if self.bigArgLen > 0:
            self.lenRequested = min(_BUFFER_SIZE, self.bigArgLen)
            return (self.receiveBigArg, self.lenRequested)
        else:
            if not self.errorOccurred:
                self.tmpfile.close()
                self.args.append((self.tmpname, self.arglen))
            else:
                self.args.append('ignored')

            if len(self.args) == self.argCount:
                if self.errorOccurred:
                    # XXX theoretically may need to call writeStatusLenValue
                    self.writeStatus("0001")
                else:
                    self.blocking = 1
                    self.factory.doOp(self)
                    self.numOps += 1
                    self.lastOp = self.args[0]
                    self.lastOpTime = time.asctime()
                return self.startState
            else:
                return (self.receiveLenArg, 20)

class ErrorValue:
    def val(self):
        return ''

    def desc(self):
        return 0

    def length(self):
        return 0

    def isLarge(self):
        return False

class FileProducer:
    def __init__(self, value, bufferSize, transport):
        self._value = value
        self._file = value.getFile()
        self._bufferSize = bufferSize
        self._transport = transport
        self._finished = False

    def stopProducing(self):
        if _DEBUG: log.msg('stopProducing called')
        if not self._finished:
            if _DEBUG: log.msg('stopProducing unregistering producer')
            try: self._file.close()
            except: pass
            self._transport.unregisterProducer()  # XXX I think this is safe
            self._finished = True
            self._value.accessComplete()
        else:
            log.msg("error: stopProducing called even though I finished")

    def resumeProducing(self):
        # read some more data from the file, a write it to the transport
        if _DEBUG: log.msg('resumeProducing called')
        if not self._finished:
            if _DEBUG: log.msg('resumeProducing reading file')
            try:
                data = self._file.read(self._bufferSize)
            except:
                e = sys.exc_info()[1]
                log.msg("caught exception " + str(e))
                data = ''

            if not data:
                if _DEBUG: log.msg('resumeProducing unregistering producer')
                try: self._file.close()
                except: pass
                self._transport.unregisterProducer()
                self._finished = True
                self._value.accessComplete()
            else:
                if _DEBUG: log.msg('resumeProducing sending data to client ' + data)
                self._transport.write(data)
        else:
            log.msg("error: resumeProducing called even though I unregistered")

    def pauseProducing(self):
        # XXX shouldn't need this, but I think we have to due to a bug in twisted
        if _DEBUG: log.msg('pauseProducing called')
