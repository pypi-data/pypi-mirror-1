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
This module implements an XMLSchemaManager. An XMLSchemaManager, handles 
globally known schemata, and allows lookup of imported and well known schemata
from it's sub-schemata.
'''
from zope.interface import implements

from rsl.interfaces import ISchemaCollection, ISchemaFactory
from rsl.misc.namespace import clark2tuple
from rsl.globalregistry import lookupimpl
from rsl.xsd.schema import XMLSchema

class XMLSchemaManager(object):
    '''
    A schema manager holds XSSchema instances for various namespaces.
    It helps to lookup types and elements in parsed schemas.
    '''
    
    implements(ISchemaCollection)
    
    def __init__(self, parent=None):
        '''
        initialise this schema manager.
        the parent manager is asked, if the manager itself does not know
        a requested schema. If parent is none, then this manager is the 
        root manager.
        '''
        self.parent = parent
        self.schemas = {}
        
    def loadStandardSchema(self, namespace):
        '''
        If an xml schema is found nowhere else, try to find a registered
        ISchemaFactory which may provide the requested namespace url.
        This function is only executed in the root schema manager.
        '''
        # first look for registered schema factories
        xsdf = lookupimpl(ISchemaFactory, namespace)
        if xsdf is not None:
            self.addSchema(xsdf(self))

    def addSchema(self, schema):
        '''
        Add an ISchema instance to this schema manager.
        '''
        self.schemas[schema.targetnamespace] = schema
        schema.manager = self
    
    def getElement(self, nameref):
        '''
        Find an xsd-element instance by named reference in clark notation.
        
        @todo: this code is duplicated in XMLSchema
        '''
        xns, name = clark2tuple(nameref)
        xmls = self.getSchema(xns)
        if name in xmls.elements:
            return xmls.elements[name]
        raise KeyError('Element %s in namespace %s not found' % (name, xns))
    
    def getType(self, nameref):
        '''
        Find an xsd-type instance by named reference in clark notation.
        
        @todo: this code is duplicated in XMLSchema
        '''
        xns, name = clark2tuple(nameref)
        xmls = self.getSchema(xns)
        if name in xmls.types:
            return xmls.types[name]
        raise KeyError('Type %s in namespace %s not found' % (name, xns))
    
    def getAttribute(self, nameref):
        '''
        Find an xsd-attribute instance by named reference in clark notation.
        
        @todo: this code is duplicated in XMLSchema
        '''
        xns, name = clark2tuple(nameref)
        xmls = self.getSchema(xns)
        if name in xmls.attributes:
            return xmls.attributes[name]
        raise KeyError('Attribute %s in namespace %s not found' % (name, xns))
    
    def getGroup(self, nameref):
        '''
        Find an xsd-group instance by named reference in clark notation.
        
        @todo: this code is duplicated in XMLSchema
        '''
        xns, name = clark2tuple(nameref)
        xmls = self.getSchema(xns)
        if name in xmls.groups:
            return xmls.groups[name]
        raise KeyError('Group %s in namespace %s not found' % (name, xns))
    
    def getSchema(self, namespace):
        '''
        Find a registered ISchema instance by namespace. If it is not found in
        this schema manager, then the parent schema manager is asked. If the
        root schema manager does not know it, it tries to find a registered
        ISchemaFactory for this namespace.
        
        @todo: this code is duplicated in XMLSchema
        '''
        if namespace in self.schemas:
            return self.schemas[namespace]
        if self.parent:
            return self.parent.getSchema(namespace)
        # ok... here we normally should be in the globalschemamanger, look for 
        #       standard schemas to load
        self.loadStandardSchema(namespace)
        return self.schemas[namespace]
        #raise KeyError('Schema %s not found' % (namespace))
    
    def parseSchema(self, schema_tree):
        '''
        This function takes an etree representing a schema file 
        and adds the containing schemas to this schema manager
        '''
        schema = XMLSchema(schema_tree, self)
        self.addSchema(schema)
        
# there is one globalSchemaManager, which is currently used by 
# e.g.: SchemaReference to resolve types and elements.
# another purpose for this global manager is, to save resources and load
# standard schemas only once.
GLOBALSCHEMAMANAGER = XMLSchemaManager()
