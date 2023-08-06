##############################################################################
# Copyright 2008, Gerhard Weis
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#  * Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#  * Neither the name of the authors nor the names of its contributors
#    may be used to endorse or promote products derived from this software
#    without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR 
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT
##############################################################################
'''
this module defines data types to be used by xml-deserialisers. those data 
types are derived from the standard python builtin data types, and are able to
store xml-attributes as object-attributes.
'''

class ValueType(object):
    '''
    base type for deserialtypes.
    '''
    
    def __eq__(self, other):
        '''
        override equality test. this method allows to compare the bultin
        data types with the derived ones as usual. it consideres an 
        eventually available __dict__ attribute in its comparison.
        '''
        ############
        # mydict... otherdict
        #  0           NA        True
        #  0           AVAIL     Cmp
        #  1           NA        False
        #  1           AVAIL     Cmp
        if other is None:
            return False
        supcls = super(ValueType, self)
        if hasattr(supcls, '__eq__'):
            ret = supcls.__eq__(other) # py 2.5
        else:
            ret = (supcls.__cmp__(other) == 0) # py 2.4
        if ret:
            if hasattr(other, '__dict__'):
                ret = self.__dict__ == other.__dict__
            else:
                ret = not bool(self.__dict__)
        return ret
    
    def __ne__(self, other):
        '''
        override non equality test. this method allows to compare the 
        bultin data types with the derived ones as usual. it consideres an 
        eventually available __dict__ attribute in its comparison.
        '''
        ############
        # mydict... otherdict
        #  0           NA        False
        #  0           AVAIL     Cmp
        #  1           NA        True
        #  1           AVAIL     Cmp
        if other is None:
            return True
        supcls = super(ValueType, self)
        if hasattr(supcls, '__ne__'):
            ret = supcls.__ne__(other) # py 2.5
        else:
            ret = (supcls.__cmp__(other) != 0) # py 2.4
        if not ret:
            if hasattr(other, '__dict__'):
                ret = self.__dict__ != other.__dict__
            else:
                ret = bool(self.__dict__)
        return ret
    
    def __repr__(self):
        '''
        show an eventually available __dict__ attribute in repr output.
        '''
        if self.__dict__:
            return super(ValueType, self).__repr__() + ',' + repr(self.__dict__)
        else:
            return super(ValueType, self).__repr__()

class Dict(ValueType, dict):
    '''
    the builtin compatible dict type with additional meta infos (xml-attributes).
    '''

class List(ValueType, list):
    '''
    the builtin compatible list type with additional meta infos (xml-attributes).
    '''

class String(ValueType, str):
    '''
    the builtin compatible string type with additional meta infos (xml-attributes).
    '''

class Unicode(ValueType, unicode):
    '''
    the builtin compatible unicde type with additional meta infos (xml-attributes).
    '''
