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

# to do: uniformally cope with get encodings... 

import os, operator
from cgi import escape
from urllib import quote_plus
attrEscape = escape

from twisted.internet import defer
from twisted.web import resource, server, static
from twisted.python import log

from nwss.dummyComm import *
from nwss.babelConfig import monitorEngines

import nwss.config

_PythonFP =     0x01000000
_DirectString = 0x00000001
_DEBUG = 0

# modified from twisted's default web file serving.
styleBlock = '''\
<style>
  ul.menu {
    display: block;
    padding: 0 0.3em 0.3em 0.3em;
    background-color: #777;
    margin: 0 0 1em 0;
  }
  ul.menu li {
    display: inline;
    padding: 0 0 0 1em;
  }
  ul.menu a:hover {
    background-color: black;
    text-decoration: none;
  }
  ul.menu a:link, ul.menu a:visited {
    color: white;
    text-decoration: none;
  }
  a:link, a:visited {
    color: blue;
    text-decoration: none;
  }
  .tableheader {
    background-color: #cecece;
  }
  .even {
    background-color: #eee;
  }
  .odd {
    background-color: #dedede;
  }
  .error {
    color: #EE1111;
    font-weight: bold;
    margin: 20;
  }
  .confirm {
    color: #EE1111;
    font-weight: bold;
    margin: 20;
  }
  .info {
    color: black;
    margin: 20;
  }
  body {
    border: 0;
    padding: 0;
    margin: 0;
    background-color: #efefef;
    font-family: helvetica, sans-serif;
  }
  h1 {
    padding: 0.3em;
    background-color: #777;
    color: white;
    font-size: 1.6em;
    font-style: italic;
    font-weight: bold;
    margin-bottom: 0;
  }
  th {
    text-align: left;
  }
  table form {
    margin-bottom: 0;
  }
  input[value=X] {
    color: #EE1111;
    font-weight: bold;
  }
  .nwstable {
    margin: 0 0 0 1em;
  }
</style>
'''

def hasAllKeys(d, klist):
    return reduce(operator.__and__, map(d.has_key, klist), True)

# here are a number of functions that generate html for error messages
def noWorkspace(wsName):
    return '''\
<html>
<head>
<title>Error</title>
%s
</head>
<body>
<h1> Error </h1>
<ul class="menu">
<li><a href="doit?op=listWss"> NetWorkSpaces </a></li>
</ul>
<div class="error"> There is currently no workspace named %s. </div>
</body>
</html>
''' % (styleBlock,
       escape(wsName))

def monitorNotRunning(monName):
    return '''\
<html>
<head>
<title>Error</title>
%s
</head>
<body>
<h1> Error </h1>
<ul class="menu">
<li><a href="doit?op=listWss"> NetWorkSpaces </a></li>
</ul>
<div class="error"> %s not running. </div>
</body>
</html>
''' % (styleBlock,
       escape(monName))

def invalidWorkSpaceSpecified(wsName):
    return '''\
<html>
<head>
<title>Error</title>
%s
</head>
<body>
<h1> Error </h1>
<ul class="menu">
<li><a href="doit?op=listWss"> NetWorkSpaces </a></li>
</ul>
<div class="error"> Invalid workspace specified for monitor: %s </div>
</body>
</html>
''' % (styleBlock,
       escape(wsName))

def variableNotInWorkspace(varName, wsName):
    return '''\
<html>
<head>
<title>Error</title>
%s
</head>
<body>
<h1> Error </h1>
<ul class="menu">
<li><a href="doit?op=listVars&wsName=%s"> Variables </a></li>
<li><a href="doit?op=listWss"> NetWorkSpaces </a></li>
</ul>
<div class="error"> No variable named "%s" currently in "%s". </div>
</body>
</html>
''' % (styleBlock,
       quote_plus(wsName),
       escape(varName), escape(wsName))

def noMonitor(monName):
    return '''\
<html>
<title>Error</title>
%s
<body>
<h1> Error </h1>
<ul class="menu">
<li><a href="doit?op=listWss"> NetWorkSpaces </a></li>
</ul>
<div class="error"> No monitor found for %s </div>
</body>
</html>
''' % (styleBlock,
       escape(monName))

def malformedRequest():
    return '''\
<html>
<head>
<title>Error</title>
%s
</head>
<body>
<h1> Error </h1>
<ul class="menu">
<li><a href="doit?op=listWss"> NetWorkSpaces </a></li>
</ul>
<div class="error"> Malformed request. </div>
</body>
</html>
''' % (styleBlock,)

def monitorError(msg):
    return '''\
<html>
<head>
<title>Error</title>
%s
</head>
<body>
<h1> Error </h1>
<ul class="menu">
<li><a href="doit?op=listWss"> NetWorkSpaces </a></li>
</ul>
<div class="error"> Error monitoring workspace: %s </div>
</body>
</html>
''' % (styleBlock,
       escape(str(msg)))

def staticServerError(dirname):
    return '''\
<html>
<head>
<title>Error</title>
%s
</head>
<body>
<h1> Error </h1>
<ul class="menu">
<li><a href="doit?op=listWss"> NetWorkSpaces </a></li>
</ul>
<div class="error"> Cannot server files from directory "%s". </div>
</body>
</html>
''' % (styleBlock,
       escape(dirname))

def wsDeleted(wsName):
    return '''\
<html>
<head>
<meta http-equiv="Refresh" content="3;URL=doit?op=listWss"> 
<title>Workspace Deleted</title>
%s
</head>
<body>
<h1> Info </h1>
<ul class="menu">
<li><a href="doit?op=listWss"> NetWorkSpaces </a></li>
</ul>
<div class="info"> NetWorkSpace "%s" was deleted. </div>
</body>
</html>
''' % (styleBlock,
       escape(wsName))

def varDeleted(wsName, varName):
    return '''\
<html>
<head>
<meta http-equiv="Refresh" content="3;URL=doit?op=listVars&wsName=%s&varName=%s"> 
<title>Variable Deleted</title>
%s
</head>
<body>
<h1> Info </h1>
<ul class="menu">
<li><a href="doit?op=listVars&wsName=%s"> Variables </a></li>
<li><a href="doit?op=listWss"> NetWorkSpaces </a></li>
</ul>
<div class="info"> Variable "%s" in "%s" was deleted. </div>
<p>
</body>
</html>
''' % (quote_plus(wsName), quote_plus(varName),
       styleBlock,
       quote_plus(wsName),
       escape(varName), escape(wsName))

def varFetched(wsName, varName):
    return '''\
<html>
<head>
<meta http-equiv="Refresh" content="3;URL=doit?op=showVar&wsName=%s&varName=%s"> 
<title>Variable Fetched</title>
%s
</head>
<body>
<h1> Info </h1>
<ul class="menu">
<li><a href="doit?op=showVar&wsName=%s&varName=%s"> Values </a></li>
<li><a href="doit?op=listVars&wsName=%s"> Variables </a></li>
<li><a href="doit?op=listWss"> NetWorkSpaces </a></li>
</ul>
<div class="info"> Value in variable "%s" was (possibly) removed. </div>
<p>
</body>
</html>
''' % (quote_plus(wsName), quote_plus(varName),
       styleBlock,
       quote_plus(wsName), quote_plus(varName),
       quote_plus(wsName),
       escape(varName))

class Translator:
    def __init__(self, server, request, wsName, varName, vVals):
        self.request, self.wsName, self.varName = request, wsName, varName
        request.write('''\
<html>
<head>
<title>Values in %s</title>
%s    
</head>
<body>
<h1> Values in %s </h1>
<ul class="menu">
<li><a href="doit?op=listVars&wsName=%s"> Variables </a></li>
<li><a href="doit?op=listWss"> NetWorkSpaces </a></li>
<li><a href="doit?op=confirmFetchTryVar&wsName=%s&varName=%s"> fetchTry </a></li>
<li><a href="doit?op=showVar&wsName=%s&varName=%s"> Refresh </a></li>
</ul>
<ol>
''' % (escape(varName),
       styleBlock,
       escape(varName),
       quote_plus(wsName),
       quote_plus(wsName), quote_plus(varName),
       quote_plus(wsName), quote_plus(varName)))

        self.numVals, self.pop = len(vVals), 0
        self.queue = [None for x in xrange(self.numVals)]

        # we kick off all translations here, rather than ping/pong-ing
        # them. we do this to avoid problems with the list of values
        # changing as the process unfolds.
        if 0 == self.numVals:
            self.endTranslation()
        else:
            for x in xrange(self.numVals):
                vVals[x].translate(server, self.collectTranslation, x)
            
    def collectTranslation(self, text, x):
        self.queue[x] = escape(text)
        self.pop += 1
        if self.pop == self.numVals:
            for i in xrange(0, self.numVals):
                self.request.write('''\
<li class="%s">%s</li>
''' % (['even', 'odd'][i%2], self.queue[i].replace('\n', '<p>')))
            self.endTranslation()
            
    def endTranslation(self):
        self.request.write('''\
</ol>
</body>
</html>
''')
        self.request.finish()

class Monitor:
    def __init__(self, server, request, monName, wsName, replyVarName):
        self.server = server
        self.request = request
        self.monName = monName
        self.argCount = -1
        self.error = 0
        self.replyVarName = replyVarName

        eng = [me for me in monitorEngines if me[0] == monName]
        if not eng:
            log.msg('error: no monitor found for ' + monName)
            self.request.write(noMonitor(monName))
            self.request.finish()
            return

        # 'args' is a tuple of the request arguments that the monitor
        # is interested in
        args = eng[0][3]

        self.dc = DummyConnection(self.writeStatusLenValue, peerId='Monitor')
        self.server.openWs(self.dc, 'use ws', monName, '', 'no')

        if _DEBUG: log.msg('Monitor: storing request')
        # note that this doesn't currently support multiple values for arguments
        monargs = {}
        numargs = 0
        for a in args:
            if request.args.has_key(a):
                monargs[a] = request.args[a]
                numargs += len(monargs[a])

        monargs['wsName'] = [wsName]
        monargs['replyVarName'] = [self.replyVarName]
        numargs += 2

        # note: this code assumes only one monitor process per workspace.
        # store the number of arguments, followed by the arguments
        # in NAME=VALUE form
        desc = _PythonFP | _DirectString
        self.server.setVar(self.dc, 'store', monName, 'request',
                desc, str(numargs))
        for k, vlist in monargs.items():
            assert type(vlist) == list
            for v in vlist:
                assert type(v) == str
                self.server.setVar(self.dc, 'store', monName, 'request',
                        desc, k + '=' + v)

        if _DEBUG: log.msg('Monitor: fetching reply')
        self.server.getVar(self.dc, 'fetch', monName, self.replyVarName)
        if _DEBUG: log.msg('Monitor: getVar returned')

    def writeStatusLenValue(self, (status, varId, valIndex, value)):
        if _DEBUG: log.msg('Monitor: monitor replied')
        if self.argCount < 0:
            if self.error:
                log.msg('Monitor: ignoring header count due to previous error (argCount < 0)')
            else:
                hc = value.val()
                try:
                    self.argCount = int(hc)
                except:
                    log.msg('Monitor: got bad value for header count: %s' % hc)
                    self.error = 1
                    self.request.setHeader('content-type', 'text/html')
                    self.request.write(monitorError('got bad value for header count'))
                    self.request.finish()
                else:
                    if _DEBUG: log.msg('Monitor: %d headers coming' % self.argCount)
                    self.server.getVar(self.dc, 'fetch', self.monName, self.replyVarName)
        elif self.argCount > 0:
            self.argCount -= 1
            if self.error:
                log.msg('Monitor: ignoring header due to previous error (argCount = %d)' % (self.argCount + 1,))
                self.server.getVar(self.dc, 'fetch', self.monName, self.replyVarName)
            else:
                hs = value.val()
                try:
                    k, v = [x.strip() for x in hs.split('=', 1)]
                except:
                    log.msg('Monitor: error handling header specification: %s' % hs)
                    self.error = 1
                    self.request.setHeader('content-type', 'text/html')
                    self.request.write(monitorError('error handling header specification'))
                    self.request.finish()
                else:
                    if _DEBUG: log.msg('Monitor: got a header; %s = %s' % (repr(k), repr(v)))
                    self.request.setHeader(k, v)
                    if _DEBUG: log.msg('Monitor: got a header; %d more coming' % self.argCount)
                    self.server.getVar(self.dc, 'fetch', self.monName, self.replyVarName)
        else:
            if _DEBUG: log.msg('Monitor: got the payload')
            if self.error:
                log.msg('Monitor: ignoring payload value due to previous error (argCount is 0)')
            else:
                if status:
                    # XXX this doesn't work well if the browser is expecting an image...
                    log.msg('Monitor: bad status = ' + str(status))
                    self.request.setHeader('content-type', 'text/html')
                    self.request.write(monitorError('status = %d' % status))
                else:
                    self.request.write(value.val())

                self.request.finish()

                # it will be an error if writeStatusLenValue is called again
                self.error = 1

                self.server.deleteVar(self.dc, 'delete var', self.monName, self.replyVarName);
                if _DEBUG: log.msg('Monitor: finished browser reply')

class NwsWebDynamic(resource.Resource):
    isLeaf = True # never call getChild, go to render_GET directly.

    def __init__(self, nwsServer):
        resource.Resource.__init__(self)

        self.extToInt = nwsServer.extToIntWsName
        self.spaces = nwsServer.spaces
        self.dc = DummyConnection(peerId='NwsWebDynamic')
        self.nwsServer = nwsServer
        self.monid = 0

        self.opTable = {
            'confirmDeleteVar':         self.confirmDeleteVar,
            'confirmDeleteWs':          self.confirmDeleteWs,
            'deleteVar':                self.deleteVar,
            'deleteWs':                 self.deleteWs,
            'confirmFetchTryVar':       self.confirmFetchTryVar,
            'fetchTryVar':              self.fetchTryVar,
            'listVars':                 self.listVars,
            'listWss':                  self.listWss,
            'showVar':                  self.showVar,
            'showMonitor':              self.showMonitor,
            'listMonitors':             self.listMonitors,
            'listClients':              self.listClients,
        }
            
    def confirmDeleteVar(self, request):
        try:
            varName = request.args['varName'][0]
            wsName = request.args['wsName'][0]
            confirm = '''\
<html>
<head>
<title>Confirm Variable Deletion</title>
%s
</head>
<body>
<h1> Confirm Variable Deletion </h1>
<ul class="menu">
<li><a href="doit?op=listVars&wsName=%s"> Variables </a></li>
<li><a href="doit?op=listWss"> NetWorkSpaces </a></li>
</ul>
<p>
<table border="0" cellspacing="0" cellpadding="4">
<tr><td colspan="2" class="confirm">Really delete variable "%s"?</td></tr>
<tr>
  <td align="center">
    <form action="doit" method="post">
    <input type="hidden" name="op" value="deleteVar">
    <input type="hidden" name="wsName" value="%s">
    <input type="hidden" name="varName" value="%s">
    <input type="submit" value="Yes">
    </form>
  </td>
  <td align="center">
    <form action="doit" method="get">
    <input type="hidden" name="op" value="listVars">
    <input type="hidden" name="wsName" value="%s">
    <input type="submit" value="No">
    </form>
  </td>
</tr>
</table>
</body>
</html>
''' % (styleBlock,
       quote_plus(wsName),
       escape(varName),
       attrEscape(wsName),
       attrEscape(varName),
       attrEscape(wsName))

        except Exception, e:
            log.msg('error: caught exception: %s' % str(e))
            confirm = malformedRequest()
        return confirm

    def confirmDeleteWs(self, request):
        try:
            wsName = request.args['wsName'][0]
            confirm = '''\
<html>
<head>
<title>Confirm Workspace Deletion</title>
%s
</head>
<body>
<h1> Confirm Workspace Deletion </h1>
<ul class="menu">
<li><a href="doit?op=listWss"> NetWorkSpaces </a></li>
</ul>
<table border="0" cellspacing="0" cellpadding="4">
<tr><td colspan="2" class="confirm">Really delete workspace "%s"?</td></tr>
<tr>
  <td align="center">
    <form action="doit" method="post">
    <input type="hidden" name="op" value="deleteWs">
    <input type="hidden" name="wsName" value="%s">
    <input type="submit" value="Yes">
    </form>
  </td>
  <td align="center">
    <form action="doit" method="get">
    <input type="hidden" name="op" value="listWss">
    <input type="submit" value="No">
    </form>
  </td>
</tr>
</table>
</body>
</html>
''' % (styleBlock,
       escape(wsName),
       attrEscape(wsName))

        except Exception, e:
            log.msg('error: caught exception: %s' % str(e))
            confirm = malformedRequest()
        return confirm

    def confirmFetchTryVar(self, request):
        try:
            wsName = request.args['wsName'][0]
            varName = request.args['varName'][0]
            confirm = '''\
<html>
<head>
<title>Confirm FetchTry</title>
%s
</head>
<body>
<h1> Confirm FetchTry </h1>
<ul class="menu">
<li><a href="doit?op=showVar&wsName=%s&varName=%s"> Values </a></li>
<li><a href="doit?op=listVars&wsName=%s"> Variables </a></li>
<li><a href="doit?op=listWss"> NetWorkSpaces </a></li>
</ul>
<table border="0" cellspacing="0" cellpadding="4">
<tr><td colspan="2" class="confirm">Really fetchTry (ie. remove)<br> variable "%s"?</td></tr>
<tr>
  <td align="center">
    <form action="doit" method="post">
    <input type="hidden" name="op" value="fetchTryVar">
    <input type="hidden" name="wsName" value="%s">
    <input type="hidden" name="varName" value="%s">
    <input type="submit" value="Yes">
    </form>
  </td>
  <td align="center">
    <form action="doit" method="get">
    <input type="hidden" name="op" value="showVar">
    <input type="hidden" name="wsName" value="%s">
    <input type="hidden" name="varName" value="%s">
    <input type="submit" value="No">
    </form>
  </td>
</tr>
</table>
</body>
</html>
''' % (styleBlock,
       quote_plus(wsName), quote_plus(varName),
       quote_plus(wsName),
       escape(varName),
       attrEscape(wsName),
       attrEscape(varName),
       attrEscape(wsName),
       attrEscape(varName))

        except Exception, e:
            log.msg('error: caught exception: %s' % str(e))
            confirm = malformedRequest()
        return confirm

    def deleteVar(self, request):
        try:
            varName = request.args['varName'][0]
            wsName = request.args['wsName'][0]
            bindings = self.spaces[self.extToInt[wsName]].bindings
        except KeyError:
            return variableNotInWorkspace(varName, wsName)

        self.nwsServer.openWs(self.dc, 'use ws', wsName, '', 'no')
        self.nwsServer.deleteVar(self.dc, 'delete var', wsName, varName);
        return varDeleted(wsName, varName)

    def deleteWs(self, request):
        try:
            wsName = request.args['wsName'][0]
            bindings = self.spaces[self.extToInt[wsName]].bindings
        except KeyError:
            return noWorkspace(wsName)

        self.nwsServer.deleteNetWorkSpace(self.dc, 'delete ws', wsName);
        return wsDeleted(wsName)

    def listWss(self, request):
        extWsNames = self.extToInt.keys()
        extWsNames.sort()
        setList = '''\
<html>
<head>
<title>NetWorkSpaces</title>
%s
</head>
<body>
<h1> NetWorkSpaces </h1>
<ul class="menu">
<li><a href="doit?op=listClients"> Clients </a></li>
<li><a href="doit?op=listWss"> Refresh </a></li>
</ul>
<table cellpadding="4" class="nwstable">
<tr class="tableheader">
  <th>Name</th>
  <th>Monitor</th>
  <th>Owner</th>
  <th>Persistent</th>
  <th># Variables</th>
  <th>Delete?</th>
</tr>
''' % (styleBlock,)

        for i in xrange(len(extWsNames)):
            n = extWsNames[i]
            intName = self.extToInt[n]
            b = self.spaces[intName].bindings
            monitors = [mentry for mentry in monitorEngines if hasAllKeys(b, mentry[2])]

            if len(monitors) > 1:
                setList += '''\
<tr class="%s">
  <td><a href="doit?op=listVars&wsName=%s">%s</a></td>
  <td><a href="doit?op=listMonitors&wsName=%s">list monitors</a></td>
  <td>%s</td>
  <td>%s</td>
  <td>%d</td>
  <td>
    <form action="doit" method="post">
    <input type="hidden" name="op" value="confirmDeleteWs">
    <input type="hidden" name="wsName" value="%s">
    <input type="submit" value="X">
    </form>
  </td>
</tr>
'''          % (['even', 'odd'][i%2],
                quote_plus(n), escape(n),
                quote_plus(n),
                escape(self.spaces[intName].owner),
                self.spaces[intName].persistent,
                len(b),
                attrEscape(n))
            elif len(monitors) == 1:
                monName = monitors[0][0]
                dispName = monitors[0][1]
                setList += '''\
<tr class="%s">
  <td><a href="doit?op=listVars&wsName=%s">%s</a></td>
  <td><a href="doit?op=showMonitor&wsName=%s&monName=%s">%s</a></td>
  <td>%s</td>
  <td>%s</td>
  <td>%d</td>
  <td>
    <form action="doit" method="post">
    <input type="hidden" name="op" value="confirmDeleteWs">
    <input type="hidden" name="wsName" value="%s">
    <input type="submit" value="X">
    </form>
  </td>
</tr>
'''          % (['even', 'odd'][i%2],
                quote_plus(n), escape(n),
                quote_plus(n), quote_plus(monName), escape(dispName),
                escape(self.spaces[intName].owner),
                self.spaces[intName].persistent,
                len(b),
                attrEscape(n))
            else:
                setList += '''\
<tr class="%s">
  <td><a href="doit?op=listVars&wsName=%s">%s</a></td>
  <td>[none]</td>
  <td>%s</td>
  <td>%s</td>
  <td>%d</td>
  <td>
    <form action="doit" method="post">
    <input type="hidden" name="op" value="confirmDeleteWs">
    <input type="hidden" name="wsName" value="%s">
    <input type="submit" value="X">
    </form>
  </td>
</tr>
'''          % (['even', 'odd'][i%2],
                quote_plus(n), escape(n),
                escape(self.spaces[intName].owner),
                self.spaces[intName].persistent,
                len(b),
                attrEscape(n))

        setList += '''\
</table>
</body>
</html>
'''
        return setList

    def showMonitor(self, request):
        wsName = '[wsName missing]'
        try:
            wsName = request.args['wsName'][0]
            bindings = self.spaces[self.extToInt[wsName]].bindings
        except KeyError:
            return noWorkspace(wsName)

        monName = '[monName missing]'
        try:
            monName = request.args['monName'][0]
            vbindings = self.spaces[self.extToInt[monName]].bindings
        except KeyError:
            return monitorNotRunning(monName)

        # verify that the wsName workspace qualifies to be handled by monName
        monlist = [mentry[0] for mentry in monitorEngines if hasAllKeys(bindings, mentry[2])]
        if monName not in monlist: return invalidWorkSpaceSpecified(wsName)

        Monitor(self.nwsServer, request, monName, wsName, 'reply_%d' % self.monid)
        self.monid += 1
        if self.monid > 1000000: self.monid = 0
        return server.NOT_DONE_YET

    def listMonitors(self, request):
        wsName = '[wsName missing]'
        try:
            wsName = request.args['wsName'][0]
            bindings = self.spaces[self.extToInt[wsName]].bindings
        except KeyError:
            return noWorkspace(wsName)

        monitors = [mentry for mentry in monitorEngines if hasAllKeys(bindings, mentry[2])]

        monListData = '''\
<html>
<head>
<title>Monitors for %s</title>
%s
</head>
<body>
<h1> Monitors for %s </h1>
<ul>
<li><a href="doit?op=listWss"> NetWorkSpaces </a></li>
</ul>
<p>
<ul>
''' % (escape(wsName),
       styleBlock,
       escape(wsName))

        for m in monitors:
            monListData += '''\
<li>
  <a href="doit?op=showMonitor&wsName=%s&monName=%s">%s</a>
</li>
''' % (quote_plus(wsName), quote_plus(m[0]), escape(m[1]))

        monListData += '''\
</ul>
</body>
</html>
'''
        return monListData

    def listVars(self, request):
        wsName = '<get wsName data missing>'
        try:
            wsName = request.args['wsName'][0]
            bindings = self.spaces[self.extToInt[wsName]].bindings
        except KeyError:
            return noWorkspace(wsName)

        vars = bindings.keys()
        vars.sort()
        varListData = '''\
<html>
<head>
<title>Variables in %s</title>
%s
</head>
<body>
<h1> Variables in %s </h1>
<ul class="menu">
<li><a href="doit?op=listWss"> NetWorkSpaces </a></li>
<li><a href="doit?op=listVars&wsName=%s"> Refresh </a></li>
</ul>
<p>
<table cellpadding="4" class="nwstable">
<tr class="tableheader">
  <th>Variable</th>
  <th># Values</th>
  <th># Fetchers</th>
  <th># Finders</th>
  <th>Mode</th>
  <th>Delete?</th>
</tr>
''' % (escape(wsName),
       styleBlock,
       escape(wsName),
       quote_plus(wsName))

        for i in xrange(len(vars)):
            varName = vars[i]
            var = bindings[varName]
            varListData += '''\
<tr class="%s">
  <td><a href="doit?op=showVar&wsName=%s&varName=%s">%s</a></td>
  <td align="right">%d</td>
  <td align="right">%d</td>
  <td align="right">%d</td>
  <td>%s</td>
  <td>
    <form action="doit" method="post">
    <input type="hidden" name="op" value="confirmDeleteVar">
    <input type="hidden" name="wsName" value="%s">
    <input type="hidden" name="varName" value="%s">
    <input type="submit" value="X">
    </form>
  </td>
</tr>
'''      % (['even', 'odd'][i%2],
            quote_plus(wsName), quote_plus(varName), escape(varName),
            len(var.values),
            len(var.fetchers),
            len(var.finders),
            var.mode,
            attrEscape(wsName),
            attrEscape(varName))

        varListData += '''\
</table>
</body>
</html>
'''

        return varListData

    def showVar(self, request):
        wsName, varName = '<get wsName data missing>', '<get varName data missing>'
        try:
            wsName, varName = request.args['wsName'][0], request.args['varName'][0]
            vVals = self.spaces[self.extToInt[wsName]].bindings[varName].values
        except KeyError:
            return variableNotInWorkspace(varName, wsName)

        Translator(self.nwsServer, request, wsName, varName, vVals)
        return server.NOT_DONE_YET

    def fetchTryVar(self, request):
        wsName, varName = request.args['wsName'][0], request.args['varName'][0]
        self.nwsServer.openWs(self.dc, 'use ws', wsName, '', 'no')
        self.nwsServer.getVar(self.dc, 'fetchTry', wsName, varName)
        return varFetched(wsName, varName)

    def listClients(self, request):
        clientListData = '''\
<html>
<head>
<title>Clients</title>
%s
</head>
<body>
<h1> Clients </h1>
<ul class="menu">
<li><a href="doit?op=listWss"> NetWorkSpaces </a></li>
<li><a href="doit?op=listClients"> Refresh </a></li>
</ul>
<p>
<table cellpadding="4" class="nwstable">
<tr class="tableheader">
  <th>Client</th>
  <th>Session #</th>
  <th># Ops</th>
  <th># Long Values</th>
  <th># Wss Owned</th>
  <th>Last Op</th>
  <th>Blocking</th>
  <th>Ws and var</th>
  <th>Time of Last Op</th>
</tr>
''' % (styleBlock,)

        i = 0
        for p in self.nwsServer._factory._protocols.values():
            clientListData += '''\
<tr class="%s">
  <td>%s</td>
  <td>%d</td>
  <td>%d</td>
  <td>%d</td>
  <td>%d</td>
  <td>%s</td>
  <td>%s</td>
  <td>%s</td>
  <td>%s</td>
</tr>
'''         % (['even', 'odd'][i%2],
                escape(p.peer),
                p.sessionno,
                p.numOps,
                p.numLongValues,
                len(p.mySets),
                escape(p.lastOp),
                p.blocking and "True" or "False",
                p.blockingVar and p.blockingVar.getName() or "",
                escape(p.lastOpTime))
            i += 1

        clientListData += '''\
</table>
</body>
</html>
'''
        return clientListData

    def render_GET(self, request):
        request.setHeader('cache-control', 'no-cache')
        return self.opTable.get(request.args.get('op', ['listWss'])[0], self.listWss)(request)

    def render_POST(self, request):
        request.setHeader('cache-control', 'no-cache')
        return self.opTable.get(request.args.get('op', ['listWss'])[0], self.listWss)(request)

class NwsWeb(resource.Resource):
    def __init__(self, nwsServer):
        resource.Resource.__init__(self)

        self.dynamic = NwsWebDynamic(nwsServer)

        log.msg('clientCode served from directory ' + nwss.config.nwsWebServedDir)
        if os.path.isdir(nwss.config.nwsWebServedDir):
            cc = static.File(nwss.config.nwsWebServedDir)
            cc.contentTypes.update({
                '.m': 'text/plain', '.M': 'text/plain',
                '.py': 'text/plain', '.PY': 'text/plain',
                '.r': 'text/plain', '.R': 'text/plain'})
        else:
            log.msg("clientCode directory doesn't exist")
            cc = static.Data(staticServerError(nwss.config.nwsWebServedDir), 'text/html')
        self.putChild('clientCode', cc)
            
        
    def getChild(self, name, request):
        return self.dynamic
