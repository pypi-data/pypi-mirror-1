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
This module provides an implementation of XSD-urtypes.
'''
from rsl.xsd.deserialtypes import Unicode

################################################
# Schema built-int types:
#      the first 2 are the so called ur-types
################################################

class AnyType(object):
    '''
    This is the base type for all schema types.
    '''
    
    def __init__(self, name, xsd):
        '''
        init type. needs local name and xsd where it is defined in.
        '''
        self.name = name
        self.xsd = xsd
    
    def getsubelementnames(self, visited=None):
        '''
        return the names of subelements if any.
        
        visited is used to handle recursive structures.
        '''
        return []
    
    def gettypename(self):
        '''
        return type name tuple (nsurl, name)
        '''
        return self.xsd.targetnamespace, self.name

class AnySimpleType(AnyType):
    '''
    This is the base type for all simple types.
    '''
    
    def getelement(self):
        '''
        return xsd-element instance.
        
        TODO: should be none here shouldn't it?
        '''
        return self
    
    def encode(self, data):
        '''
        it is used to convert the given data to a string
        '''
        return unicode(data)
    
    def decode(self, data):
        '''
        it is used to convert the given data to a string
        '''
        return Unicode(data)
    
    def getsubelementnames(self, visited=None):
        '''
        return names of subelements.
        a simple type can not have sub elements.
        
        visited is used to handle recursive structures.
        '''
        return []
    
    def gettype(self):
        '''
        return the xsd type instance.
        '''
        return self
    
    def getattributes(self):
        '''
        return defined xsd attribute instances.
        a simple type can not have attributes.
        '''
        return None
