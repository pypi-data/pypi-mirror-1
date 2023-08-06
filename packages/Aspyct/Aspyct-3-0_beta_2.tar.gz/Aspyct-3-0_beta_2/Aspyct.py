# Copyright 2009 Antoine d'Otreppe de Bouvette
#
# This file is part of the Aspyct library. see http://www.aspyct.org
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
import re

if sys.version_info[0] == 2:
    import _Aspyct.py2x
else:
    import _Aspyct.py3x

from _Aspyct.common import Aspect, wrap

# Make all core functions available
VERSION = '3.0 beta 2'
VERSION_INFO = (3, 0)
VERSION_NAME = 'Aspyct3k beta 2'

def require(req):
    """ - where 'req' is a version string (x.x.x...)
    Raises a VersionError if required version is higher than current Aspyct version.
    This method is not available with 'from Aspyct import *' statement, to avoid name conflicts
    (This is a too frequently used name)
    """
    req = req.split('.')
    cur = VERSION_INFO
    maxI = min(len(req), len(cur))
    for i in range(0, maxI):
        r = int(req[i])
        c = int(cur[i])
        if r > c:
            raise AssertionError('Required Aspyct version is not matched')
        elif c > r:
            return
    if len(req) > len(cur):
        raise AssertionError('Required Aspyct version is not matched')

FunctionType = type(require)

AspectType = type(Aspect)

class Pointcut(list):
    def __init__(self, ns, filter, match=True):
        list.__init__(self)
        
        for item in _search(ns, re.compile(filter), match):
            wrapped = wrap(getattr(ns, item))
            setattr(ns, item, wrapped)
            self.append(wrapped)
    
    def addAspect(self, aspect, *args, **kwargs):
        if type(aspect) is AspectType:
            for item in self:
                aspect(*args, **kwargs)(item)
        else:
            for item in self:
                aspect(item)

MethodType = type(Pointcut.addAspect)

def _search(ns, regexp, match):
    all = []
    for attrName in dir(ns):
        attr = getattr(ns, attrName)
        
        # If this item is not a function, pass
        if not type(attr) in (FunctionType, MethodType):
            continue
        
        if regexp.match(attrName):
            if match:
                all.append(attrName)
        elif not match:
            all.append(attrName)
    
    return all

__all__ = ("Aspect", "Pointcut")