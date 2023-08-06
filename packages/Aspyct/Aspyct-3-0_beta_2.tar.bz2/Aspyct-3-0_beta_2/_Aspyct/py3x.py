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

from .common import  CallData, __init__

def execFunction(w, *args, **kwargs):
    func = w.__original__
    
    # Create our CallData object
    cd = CallData(w, func, # With the wrapper and the original function
                  args, kwargs) # and the arguments
    
    
    # This var counts how much aspects have been processed before an avoid raises
    count = 0
    
    # Aspects list. Using it instead of w.__aspects__ spares time
    aspectList = w.__aspects__
    
    for aspect in aspectList:
        try:
            ret = aspect.atCall(cd) # Do not test hasattr, it takes a big while
            
            if cd._CallData__change:
                cd._CallData__args, cd._CallData__kwargs = ret
                cd._CallData__change = False
            
            elif cd._CallData__avoid:
                cd._CallData__returned = ret
                break # Avoid => break the loop
        
        except BaseException as e:
            if cd._CallData__avoid:
                cd._CallData__exception = e
                break # Avoid => break the loop
            else:
                raise
        
        count += 1
    
    # If there was an avoid request, jump directly to atExit
    if not cd._CallData__avoid:
        # Try to process the function
        try:
            cd._CallData__returned = func(*cd._packArgs(), **cd._CallData__kwargs)
        # The function raised
        except BaseException as e:
            cd._CallData__exception = e
    
    
    # Create a reversed list, only with aspects whose atCall has been called
    aspectList = aspectList[:count]
    aspectList.reverse()
    
    # Process both atReturn / atRaise
    for aspect in aspectList:
        try:
            cd._CallData__change = False
            
            if cd._CallData__exception: # There is an unhandled exception
                ret = aspect.atRaise(cd)
            else:
                ret = aspect.atReturn(cd)
            
            if cd._CallData__change: # A return value change has been requested
                cd._CallData__returned = ret
                cd._CallData__exception = None
        
        except BaseException as e: # If the advice raises an exception...
            if cd._CallData__change:
                cd._CallData__returned = None
                cd._CallData__exception = e
            else:
                raise
    
    # If aspects decided to raise an exception
    if cd._CallData__exception:
        raise cd._CallData__exception
    
    return cd._CallData__returned

__init__(execFunction)
