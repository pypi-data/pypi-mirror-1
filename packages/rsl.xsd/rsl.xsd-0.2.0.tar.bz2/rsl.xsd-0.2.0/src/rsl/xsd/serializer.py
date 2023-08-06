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
this module provides implementations for IXMLSerializer and IXMLDeserializer

TODO: this module needs some refactoring. the xsd-instance itself may not be
      required to do the de/serialisation. but it may be required for other 
      type systems than xsd.
'''
from lxml import etree
from zope.interface import classProvides

from rsl.misc.namespace import clark
from rsl.xsd.interfaces import IXMLSerializer, IXMLDeserializer
from rsl.xsd.deserialtypes import List, Dict
from rsl.xsd.urtype import AnySimpleType
from rsl.xsd.component import XSElement, XSAny, XSSimpleType
from rsl.xsd.namespace import NS_XMLSCHEMA_INSTANCE

class XMLElementSerializer(object):
    '''
    de/serializer methods to start with a xsd-element definition as root.
    '''
    
    classProvides(IXMLSerializer, IXMLDeserializer)
    
    @classmethod
    def serialize(cls, params, typename, schema, root):
        '''
        params ... data structure to serialize
        typename ... element name in typesystem
        schema ... ISchema/Manager instance
        root ... append serialized date to root (etree)
        
        return newly created element
        '''
        eltype = schema.getElement(typename)
        if root is None:
            root = etree.Element(eltype.getname())
        else:
            root = etree.SubElement(root, eltype.getname())
        xstype = eltype.gettype()
        return XMLSchemaSerializer.serialize(params, xstype, schema, root)
    
    @classmethod
    def deserialize(cls, root, typename, schema):
        '''
        root ... etree element to deserialise
        typename ... the element name to start serialisation with.
        schema ... ISchema/Manager instance
        
        return python data structure representing root 
        '''
        xstype = schema.getElement(typename).gettype()
        return XMLSchemaSerializer.deserialize(root, xstype, schema)

class XMLTypeSerializer(object):
    '''
    de/serializer methods to start with a xsd-type definition as root.
    '''
    
    classProvides(IXMLSerializer, IXMLDeserializer)
    
    @classmethod
    def serialize(cls, params, typename, schema, root):
        '''
        params ... data structure to serialize
        typename ... type name in typesystem
        schema ... ISchema/Manager instance
        root ... append serialized date to root (etree)
        
        return newly created element
        '''
        xstype = schema.getType(typename)
        return XMLSchemaSerializer.serialize(params, xstype, schema, root)
    
    @classmethod
    def deserialize(cls, root, typename, xsd):
        '''
        root ... etree element to deserialise
        typename ... the type name to start serialisation with.
        schema ... ISchema/Manager instance
        
        return python data structure representing root 
        '''
        xstype = xsd.getType(typename)
        return XMLSchemaSerializer.deserialize(root, xstype, xsd)

class XMLSchemaSerializer(object):
    '''
    de/serializer methods to start with a xsd-type instance as root.
    '''
    
    #classImplements(IXMLSerializer, IXMLDeserializer)
    
    @classmethod
    def serialize(cls, params, xstype, types, root):
        '''
        this function is the entry point for the serialisation mechanism
        and just provides the IXMLSerializer interface.
        
        TODO: clarify parameter types. maybe this method is not conformant
              to the interface
        '''
        return cls._serialize(xstype, params, root)
    
    @classmethod
    def deserialize(cls, root, xstype, xsd):
        '''
        this function is the entry point for the deserialisation mechanism
        and just provides the IXMLDeserializer interface.
        
        TODO: clarify parameter types. maybe this method is not conformant
              to the interface
        '''
        return cls._deserialize(xstype, root)
    
    @classmethod
    def _serialize(cls, xstype, data, root):
        '''
        the actual serialisation method.
        xstype: an xsd-type or element instance.
        data: the python data structure to serialise
        root: the element to add the serialised data (etree)
        
        returns: nothing
        '''
        if isinstance(xstype, (AnySimpleType, XSSimpleType)):
            if data is None:
                root.set(clark(NS_XMLSCHEMA_INSTANCE, 'nil'), 'true')
            else:
                root.text = xstype.encode(data)
            return
        if isinstance(xstype, XSElement): #ComplexType):
            if xstype.getlocalname() not in data:
                return
            if xstype.maxoccurs != 1:
                eltype = xstype.gettype()
                for item in data[xstype.getlocalname()]:
                    elem = etree.SubElement(root, xstype.getname())
                    cls._serialize(eltype, item, elem)
            else:
                eltype = xstype.gettype()
                elem = etree.SubElement(root, xstype.getname())
                cls._serialize(eltype, data[xstype.getlocalname()], elem)
            return
        if isinstance(xstype, XSAny):
            if xstype.maxOccurs != 1:
                #TODO: maybe if item is a dict, then use item name to serialize
                for item in data:
                    try:
                        elem = etree.XML(item)
                    except:
                        elem = etree.SubElement(root, 'any')
                        if item is None:
                            elem.set(clark(NS_XMLSCHEMA_INSTANCE, "nil"), 
                                     "true")
                        else:
                            elem.text = str(item)
                    root.append(elem)
            else:
                try:
                    elem = etree.XML(data)
                except:
                    elem = etree.SubElement(root, 'any')
                    if data is None:
                        elem.set(clark(NS_XMLSCHEMA_INSTANCE, "nil"), "true")
                    else:
                        elem.text = str(data)
            return
        nexttype = xstype.getelement()
        if nexttype is not None:
            if isinstance(nexttype, list):
                for rectype in nexttype:
                    cls._serialize(rectype, data, root)
            else:
                cls._serialize(nexttype, data, root)
        attributes = xstype.getattributes()
        if attributes:
            for attrib in attributes:
                # TODO: let attribut only serialise a single value and do name 
                #       checking before...
                #       How to handle fixed? default? 
                if '__attrs' in data:
                    attrdata = data['__attrs']
                else:
                    attrdata = data
                attrname = attrib.getname()
                attrval = attrib.encode(attrdata)
                if attrname is not None and attrval is not None:
                    root.set(attrname, attrval)
                    
    @classmethod
    def deserialattributes(cls, xstype, elem):
        '''
        a helper function to deserialise the attributes of an etree-element.
        
        returns a dictionary of attrname-value pairs.
        '''
        ret = {}
        attributes = xstype.getattributes()
        if attributes:
            for attrib in attributes:
                attrname = attrib.getname()
                attrvalue = None
                if attrname in elem.attrib:
                    attrvalue = attrib.decode(elem.attrib[attrname])
                    ret[attrname] = attrvalue
        if ret:
            return ret
        return None
    
    @classmethod
    def _deserialize(cls, xstype, root):
        '''
        the actual deserialisation method.
        xstype: an xsd-type or element instance.
        root: the element to start deserialisation from (etree)
        
        returns: python data structure
        '''
        if root is None:
            return None
        if isinstance(xstype, (AnySimpleType, XSSimpleType)):
            return xstype.decode(root.text)
        if isinstance(xstype, XSElement):
            ret = None
            childname = xstype.getname()
            if xstype.maxoccurs != 1:
                ret = List()
                for childelem in root.findall(childname):
                    # childelem has attributes, append dict.
                    val = cls._deserialize(xstype.gettype(), childelem)
                    attr = cls.deserialattributes(xstype, childelem)
                    if attr:
                        if val is None: # TODO: ugly hack for empty elements 
                                        #       with attributes
                            val = attr
                        else: 
                            for key, attrval in attr.items():
                                setattr(val, key, attrval)
                    ret.append(val)
            else:
                childelem = root.find(childname)
                if childelem is not None:
                    # childelem has attributes, append dict
                    val = cls._deserialize(xstype.gettype(), childelem)
                    attr = cls.deserialattributes(xstype, childelem)
                    if attr:
                        if val is None: # TODO: ugly hack for empty elements 
                                        #       with attributes
                            val = attr
                        else: 
                            for key, attrval in attr.items():
                                setattr(val, key, attrval)
                    ret = val
            return ret
        if isinstance(xstype, XSAny):
            # TODO: check for multiplicity unbound
            # TODO: try to find type for element name?
            ret = None
            if xstype.maxoccurs != 1:
                ret = List()
                for childelem in root:
                    ret.append(cls._deserialize(xstype.gettype(), childelem))
            else:
                childelem = root[0]
                ret = cls._deserialize(xstype.gettype(), childelem)
            return ret
        nexttype = xstype.getelement()
        if nexttype is None:
            return None
        if isinstance(nexttype, list):
            nexttype = cls.flatten(nexttype)
            ret = Dict()
            for rectype in nexttype: # TODO: possibly create map here
                ret[rectype.getlocalname()] = cls._deserialize(rectype, root)
            if len(nexttype) == 1:
                ret = ret.values()[0]
            return ret
        else:
            return cls._deserialize(nexttype, root)
      
    @classmethod
    def flatten(cls, seq):
        '''
        flattens a list of lists/tuples to a single list.
        '''
        res = []
        for item in seq:
            if (isinstance(item, (tuple, list))):
                res.extend(cls.flatten(item))
            else:
                res.append(item)
        return res  
