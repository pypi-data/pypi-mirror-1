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
This module provides an ISchema implementation for xsd-schemas to be used in 
rsl.
'''
# Note: Types with XS at the beginning are structure elements
#       Types without XS are actual instances of structure types and are only 
#       used to implement XSD built-int types

# TODO: Null handling:
#       if parameter is absent then don't add element
#       if parameter is None and element is nillable: use xsi:nil
#       if parameter is None and element is not nillable: don't add element
#                    or throw exception

# NOTES: schema: elementformDefault (default = unqualified)
#           unqualified: only root element is qualified by namespace, all 
#                        childs are unqualified.
#           qualified: all elements are qualified (either explicit or with 
#                      default namespace)

# TODO: * there are some problems in the class hierarchy from components and
#         XSAnnotated. It is not possible for XMLSchema to call super.__init__
#       * rework schema include and schema import   

import warnings
import urllib2
import urlparse

from lxml import etree
from zope.interface import implements

from rsl.interfaces import ISchema
from rsl.misc.namespace import clark2tuple
from rsl.xsd.urtype import AnyType
from rsl.xsd.component import XSAnnotated, XSElement, XSComplexType, XSGroup
from rsl.xsd.component import XSAttribute, XSSimpleType
from rsl.xsd.namespace import NS_XMLSCHEMA, NS_XMLSCHEMA_99
    
class ComplexType(AnyType):
    '''
    This may become the base type for all schema types.
    '''
    # Any and Element could be derived from this
    #TODO: implement and use this class or drop it

class XMLSchema(XSAnnotated):
    ''' 
    This is the top level Schema representation. (<schema> ... </schema>)
    '''
    
    implements(ISchema)
  
    def __init__(self, manager=None, uri=None):
        '''
        initialise a blank XMLSchema instance.
        '''
        self.manager = manager
        self.uri = uri
        self.attributeformdefault = 'unqualified'
        self.elementformdefault = 'unqualified'
        self.targetnamespace = None
        self.types = {}
        self.elements = {}
        self.groups = {}
        self.attributes = {}
        self.attributegroups = {}
        self.annotations = {}
            
    def frometree(self, schemaelem):
        '''
        load all data from schemaelem (etree) into this instance.
        
        this method does all the preparations and reads in data on
        <schema> element, and passes the actual work to _parseSchema
        '''
        super(XMLSchema, self).frometree(schemaelem)
        if schemaelem is not None:
            self.attributeformdefault = schemaelem.get("attributeFormDefault", 
                                                       'unqualified')
            self.elementformdefault = schemaelem.get("elementFormDefault", 
                                                     'unqualified')
            self.targetnamespace = schemaelem.get("targetNamespace")
        else:
            self.attributeformdefault = "unqualified"
            self.elementformdefault = "unqualified"
        if schemaelem is not None:
            self._parseSchema(schemaelem)
        return self
    
    def _parseSchema(self, schemaelem):
        '''
        parse all schema definitions contained in the etree schemaelem.
        '''
        for elem in schemaelem.getchildren():
            if elem.tag == etree.Comment:
                continue # Ingore comments
            elemns, elemname = clark2tuple(elem.tag)
            if elemns in (NS_XMLSCHEMA, NS_XMLSCHEMA_99):
                if elemname == "element":
                    self.elements[elem.get("name")] = XSElement(elem, self)
                elif elemname == "complexType":
                    self.types[elem.get("name")] = XSComplexType(elem, self)
                elif elemname == "import":
                    namespace = elem.get("namespace")
                    schemalocation = elem.get("schemaLocation")
                    # namespace must be different from current targetNamespace
                    # if namespace is non current targetNamespace must be set
                    # namespace must be equal to imported namespace
                    # if namespace is not set, imported schema must no have a 
                    #     targetNamespace
                    if namespace:
                        if namespace == self.targetnamespace:
                            raise Exception("can't import schema with the same \
                                             namespace as targetNamespace")
                        try:
                            if self.getSchema(namespace):
                                # Do nothing schema already imported:
                                # TODO implement schema merging
                                #warnings.warn('Import: schema merge not \
                                #              implemented ' + str(elem.attrib))
                                continue
                        except KeyError:
                            # if we don't find the schema try to import it
                            pass
                    if schemalocation:
                        # TODO: schemaLocation may be id-reference (#xxx) to 
                        #       other schema element in this document
                        #       or even something like (proto://addr/file#xxx)
                        #        ... so # must be split and retreived other
                        try:
                            impuri = urlparse.urljoin(self.uri, schemalocation)
                            fobj = urllib2.urlopen(impuri)
                            importtree = etree.parse(fobj)
                            fobj.close()
                            importxsd = XMLSchema(self.manager, uri=impuri)
                            importxsd.frometree(importtree.getroot())
                            if namespace:
                                if namespace != importxsd.targetnamespace:
                                    warnings.warn("namespace and \
                                        targetNamespace of imported schema must \
                                        be equal (%s, %s)" % 
                                        (namespace, importxsd.targetnamespace))
                            if self.manager is not None:
                                self.manager.addSchema(importxsd)
                            else:
                                warnings.warn('can not import schema, beause \
                                             there is no local schema manager')
                        except OSError:
                            warnings.warn("can not import schema because I \
                                           can't open location.")
                            
                    else:
                        #warnings.warn("Don't know how to import namespace \
                        #        '%s' from '%s'" % (namespace, schemaLocation))
                        pass
                elif elemname == "include":
                    schemalocation = elem.get("schemaLocation")
                    if schemalocation:
                        includeuri = urlparse.urljoin(self.uri, schemalocation)
                        includetree = etree.parse(includeuri)
                        includexsd = XMLSchema(self.manager, includeuri)
                        includexsd.frometree(includetree.getroot())
                        # TODO: elements from include has to be really included
                        if includexsd.targetnamespace is not None and \
                           includexsd.targetnamespace != self.targetnamespace:
                            raise Exception('include different namespace \
                                             not allowed')    
                    warnings.warn("Include: schema merge not implemented " + 
                                  str(elem.attrib))
                elif elemname == "group":
                    self.groups[elem.get("name")] = XSGroup(elem, self)
                elif elemname == "simpleType":
                    self.types[elem.get("name")] = XSSimpleType(elem, self)
                elif elemname == "attributeGroup":
                    pass # ignore attributeGroup for now
                    #self.attributegroups[elem.get("name")] = \
                    #    XSAttributeGroup(elem)
                elif elemname == "notation":
                    pass # ignore notation for now
                    #self.notations[elem.get("name")] = XSNotation(elem)
                elif elemname == "attribute":
                    self.attributes[elem.get("name")] = XSAttribute(elem, self)
                else:
                    warnings.warn("Schemaelement : " + elem.tag + 
                                  " not implemented")
            else:
                raise Warning("Schemanamespace : " + elemns + " not supported.")
        
    def tostring(self):
        '''
        return a nice string representation of this schema to print on stdout.
        '''
        ret = ''
        for xns, xstype in self.types.items():
            ret += "%s => %s\n" % (xns, xstype)
        for xns, xselem in self.elements.items():
            ret += "%s => %s\n" % (xns, xselem)
        return ret
    
    def getElement(self, nameref):
        '''
        Find an xsd-element instance by named reference in clark notation.
        
        @todo: this code is duplicated in XMLSchemaManager        
        '''
        xns, name = clark2tuple(nameref)
        xmls = self.getSchema(xns)
        if name in xmls.elements:
            return xmls.elements[name]
        raise KeyError('Element %s in namespace %s not found' % (name, xns))
    
    def getType(self, nameref):
        '''
        Find an xsd-type instance by named reference in clark notation.
        
        @todo: this code is duplicated in XMLSchemaManager
        '''
        xns, name = clark2tuple(nameref)
        xmls = self.getSchema(xns)
        if name in xmls.types:
            return xmls.types[name]
        raise KeyError('Type %s in namespace %s not found' % (name, xns))
    
    def getAttribute(self, nameref):
        '''
        Find an xsd-attribute instance by named reference in clark notation.
        
        @todo: this code is duplicated in XMLSchemaManager
        '''
        xns, name = clark2tuple(nameref)
        xmls = self.getSchema(xns)
        if name in xmls.attributes:
            return xmls.attributes[name]
        raise KeyError('Attribute %s in namespace %s not found' % (name, xns))
    
    def getGroup(self, nameref):
        '''
        Find an xsd-group instance by named reference in clark notation.
        
        @todo: this code is duplicated in XMLSchemaManager
        '''
        xns, name = clark2tuple(nameref)
        xmls = self.getSchema(xns)
        if name in xmls.groups:
            return xmls.groups[name]
        raise KeyError('Group %s in namespace %s not found' % (name, xns))
    
    def getSchema(self, namespace):
        '''
        Find a schema by namespace. If it is not this schema, ask the parent
        manager to retrieve it.
        '''
        if self.targetnamespace == namespace:
            return self
        if self.manager:
            return self.manager.getSchema(namespace)
        raise KeyError('Schema %s not found' % (namespace))
