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
from inspect import getmro

def copy(wrapper, wrapped):
    if hasattr(wrapped, '__module__'):
        setattr(wrapper, '__module__', wrapped.__module__)
    if hasattr(wrapped, "im_class"):
        setattr(wrapper, "im_class", wrapped.im_self)
    
    setattr(wrapper, '__name__', wrapped.__name__)
    setattr(wrapper, '__doc__', wrapped.__doc__)

FunctionType = type(copy)

execFunction = None
def __init__(func):
    global execFunction
    execFunction = func

def wrap(func):
    'Do not use this function directly'
    
    # Check whether this function is already a wrapper
    try:
        func.__aspects__
        return func
    except:
        pass
    
    # Create our wrapper
    def wrapper(*args, **kwargs):
        # Do not return an object: it causes bugs for method
        return execFunction(wrapper, *args, **kwargs)
    
    # Copy some attributes from function to wrapper (name, module etc.)
    copy(wrapper, func)
    
    # Create an aspect list
    wrapper.__aspects__ = []
    
    # And keep the original function
    wrapper.__original__ = func
    
    # Specify we wrapped a function (needed for the CallData object)
    wrapper.__ismethod__ = None
    
    return wrapper


class CallData:
    def __init__(self, w, f, args, kwargs):
        self.__func = f
        self.__kwargs = kwargs
        self.__returned = None
        self.__exception = None
        
        if w.__ismethod__ is None: # First call of this function
            # Find out whether it's a method or a function
            try:
                if getattr(args[0], f.__name__).__original__ is f:
                    w.__ismethod__ = True
                else:
                    w.__ismethod__ = False
            except:
                w.__ismethod__ = False
            
        
        if w.__ismethod__:
            slf = args[0]
            args = args[1:]
        else:
            slf = None
        
        self.__self = slf
        self.__args = args
        
        self.__avoid = False
        self.__change = False
    
    def getFunction(self):
        return self.__func
    function = property(getFunction)
    
    def getSelf(self):
        return self.__self
    self = property(getSelf)
    
    def getArgs(self):
        return tuple(self.__args)
    args = property(getArgs)
    
    def getKwargs(self):
        return self.__kwargs.copy()
    kwargs = property(getKwargs)
    
    def getReturned(self):
        return self.__returned
    returned = property(getReturned)
    
    def getException(self):
        return self.__exception
    exception = property(getException)
    
    def _packArgs(self):
        if self.__self == None:
            return self.__args
        else:
            return (self.__self, ) + self.__args
    
    def exceptionIs(self, cls):
        if self.__exception == None:
            return False
        else:
            return cls in getmro(self.__exception.__class__)
    
    def avoid(self):
        self.__avoid = True
    
    def change(self):
        self.__change = True

class Aspect(object):
    def __call__(self, func):
        wrapped = wrap(func)
        wrapped.__aspects__.insert(0, self)
        return wrapped
    
    def atCall(self, cd): pass
    def atRaise(self, cd): pass
    def atReturn(self, cd): pass
