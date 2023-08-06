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
this module defines all builtin xsd simple types.
'''
import base64
import binascii

from rsl.misc.isodate import parse_datetime
from rsl.misc.tzinfo import Local
from rsl.xsd.urtype import AnySimpleType

#normalizedString: remove line feeds, carriage returns, and tab characters.
#token: remove line feeds, carriage returns, tabs, leading and trailing spaces,
#       and multiple spaces.

# TODO: Type Hierarchy
#       * some types have nice restrictions.. short, int, long, aso... 
#         (really necessary for me?). those types are normally derived from 
#         the built-in basic types and could be parsed as is from schema for 
#         non-derived (from ur-types derived) types this is not really possible
# TODO: maybe restrict string representation of various types to those defined 
#       in xsd-standard.
#       e.g. int/Interger mayb only cover a specific value range. error if 
#            value is outside.

class IntegerType(AnySimpleType):
    '''
    This represents the xsd-integer type.
    '''
    
    def decode(self, data):
        '''
        converts the given string to a python int.
        '''
        return int(data)
    
class FloatType(AnySimpleType):
    '''
    This represents the xsd-float type.
    '''
    
    def decode(self, data):
        '''
        converts the given string to a python float.
        '''
        return float(data)

class BooleanType(AnySimpleType):
    '''
    This represents the xsd-bool type.
    '''
    
    def encode(self, data):
        '''
        convert python bool to string.
        
        TODO: which encoding type to use? '1'/'0' or 'true'/'false'?
        '''
        return str(data is True).lower()
    
    def decode(self, data):
        '''
        convert string to python bool.
        '''
        return bool(data)
    
class Base64Type(AnySimpleType):
    '''
    the xsd-base64 type.
    '''
    
    def encode(self, data):
        '''
        encode python string to base64 string.
        '''
        return base64.b64encode(data)
    
    def decode(self, data):
        '''
        decode base64 data to python string.
        '''
        return base64.b64decode(data)
    
class HexBinaryType(AnySimpleType):
    '''
    the xsd - hexbinary type.
    '''
    
    def encode(self, data):
        '''
        convert python string to hexbinary representation.
        '''
        return binascii.hexlify(data)
    
    def decode(self, data):
        '''
        convert hexbinary representation to python string.
        '''
        return binascii.unhexlify(data)
    
class DateTimeType(AnySimpleType):
    '''
    the xsd-datetime type.
    '''
    
    def preparedatetime(self, data):
        ''' apply tzinfo and convert data to datetime if possible 
        time ... provides tuples and floating point numbers
        datetime ... date, time, datetime objects
        calendar ... Calendar objects
        
        if there is no tzinfo in date/time object assume local time
        
        @todo: currently only datetime objects are supported 
        '''
        newdate = data
        if newdate.tzinfo is None:
            newdate = newdate.replace(tzinfo=Local)
        return newdate
            
    
    def encode(self, data):
        '''
        convert datetime instance to string (iso8601).
        '''
        return self.preparedatetime(data).isoformat()
    
    def decode(self, data):
        '''
        parse iso-date to datetime instance.
        '''
        return parse_datetime(data)
    
class DateType(DateTimeType):
    '''
    the xsd-date type.
    '''

    def encode(self, data):
        '''
        convert datetime object to string according to xsd-standard.
        '''
        return self.preparedatetime(data).strftime('%Y-%m-%d%z')

class TimeType(DateTimeType):
    '''
    the xsd-time type.
    '''

    def encode(self, data):
        '''
        convert datetime object to string according to xsd-standard.
        '''
        return self.preparedatetime(data).isoformat()[11:]
