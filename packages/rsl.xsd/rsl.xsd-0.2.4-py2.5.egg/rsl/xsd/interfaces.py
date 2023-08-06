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
from zope.interface import Interface

class IXMLSerializer(Interface):
    '''
    defines the method signature to serialize python data types to xml 
    according to xsd definition.
    '''
    
    def serialize(data, typename, schema, root):
        '''
        data ... data structure to turn into xml
        typename ... the schema name to start with
        schema ... an ISchema which knows about all types
        root ... the root element to add the serialized data
        
        returns the newly create element.
        '''
        
class IXMLDeserializer(Interface):
    '''
    defines the method signature to serialize xml to python data structures
    with the help of schema definitions.
    '''
    
    def deserialize(datatree, typename, schema):
        '''
        datatree ... some data structure which can be deserialized according to typename
        typename ... the schema name to start with
        schema ... an ISchema which knows all types
        
        returns a data structure representing the parse xml
        '''
