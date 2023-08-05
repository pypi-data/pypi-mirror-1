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

# these dummy classes are used by the objects that want to pretend
# they are clients of the nws server.

from twisted.python import log

_DEBUG = 0

class DummyTransport:
    def __init__(self): return

    def write(self, data):
        if _DEBUG:
            log.msg("DummyTransport.write: data = %s" % repr(data))

class DummyConnection:
    def __init__(self, wslv = None, peerId = '[Web Interface]'):
        self.mySets, self.peer, self.wsMap = [], peerId, {}
        self.transport = DummyTransport()
        if not wslv:
            self.writeStatusLenValue = self.dummyWslv
        else:
            self.writeStatusLenValue = wslv

    def __str__(self):
        return 'DummyConnection[%s]' % self.peer

    def dummyWslv(self, (status, varId, valIndex, value)):
        pass

    def writeStatus(self, status):
        pass
