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

def matlabTranslationCallback(d, v):
    d.callback(v[:-2]) # strip new lines.

def passThroughTranslationCallback(d, v):
    d.callback(v)

babelEngines = {1: ('Python babelfish', passThroughTranslationCallback),
                2: ('Matlab babelfish', matlabTranslationCallback),
                3: ('R babelfish', passThroughTranslationCallback),
                4: ('Perl babelfish', passThroughTranslationCallback),
                5: ('Ruby babelfish', passThroughTranslationCallback),
                6: ('Octave babelfish', passThroughTranslationCallback),
		7: ('Java babelfish', passThroughTranslationCallback),
		8: ('CSharp babelfish', passThroughTranslationCallback),
		9: ('ObjC babelfish', passThroughTranslationCallback)}

monitorEngines = (
    ('Sleigh Monitor', 'Sleigh Monitor',
        ('nodeList', 'totalTasks', 'rankCount', 'workerCount'),
        ('imagefile',)
    ),
    ('Nws Utility', 'Nws Utility',
        ('enableNwsUtility',),
        ('varName', 'value')
    ),
    ('Nws Configurator', 'Nws Configurator',
        ('enableNwsConfigurator',),
        ('varName', 'value')
    ),
    ('chat example', 'Chat Service',
        ('chat',),
        ('msg', 'from')
    ),
)
