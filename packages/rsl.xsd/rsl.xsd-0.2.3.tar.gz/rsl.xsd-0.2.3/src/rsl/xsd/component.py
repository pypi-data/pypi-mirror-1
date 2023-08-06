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
this module defines all structural elements of the xsd standard.

@todo: probably all of this classes here need some rework, to make them more
       complete to the standard.

@todo: does getsubelementnames also return attributes names? if yes, then 
       this method needs to be renamed
       
@todo: split this module into smaller pieces
'''
import logging
log = logging.getLogger('rsl.xsd')

from rsl.misc.namespace import clark, qname2clark, clark2tuple
from rsl.xsd.urtype import AnyType
from rsl.xsd.namespace import NS_XMLSCHEMA, NS_XMLSCHEMA_99

def multiplicity(occurs):
    '''
    handle xsd maxOccurs/minOccurs attributes.
    '''
    if occurs is None:
        return 1
    if occurs in ("unbounded", "*"): # * is not mentioned in standard i think
        return -1
    return int(occurs)

############################################################
##  Structure types
############################################################

class XSAnnotation(object):
    '''
    implementation of <annotation> element.
    '''
    
    def __init__(self, element):
        '''
        parse child elements or ignore content for now.
        '''
        self.content = None
        for child in element.getchildren():
            if child.tag in self.allowed_content:
                self.content = self.allowed_content[child.tag](child)
            elif child.tag in self.ignore_content:
                continue
            else:
                log.warn("XSAnnotation: Schemaelement " + child.tag + 
                              " not implemented")
            
class XSDocumentation(object):
    '''
    implementation of <documentation> element.
    '''
    
    def __init__(self, element):
        '''
        just store text.
        '''
        self.text = element.text

class XSAnnotated(object):
    '''
    Base class for structure types.
    Every structure type can have Annotations
    '''
    
    def __init__(self, element, xsd):
        '''
        initialise this instance and parse annotation elements.
        '''
        super(XSAnnotated, self).__init__()
        self.xsd = xsd
        self.annotations = None
        self._name = None
        self.frometree(element)
        
    def frometree(self, element):
        '''
        parse annotation child elements.
        parse name attribute
        '''
        if element is None:
            return
        self._name = element.get("name")
        self.findannotations(clark(NS_XMLSCHEMA, "annotation"), element)
        self.findannotations(clark(NS_XMLSCHEMA_99, "annotation"), element)
        return self
            
    def findannotations(self, tag, element):
        '''
        find all elements named tag (currently only "annotation") and store
        it in the instance.
        '''
        for child in element.findall(tag):
            if not self.annotations:
                self.annotations = []
            self.annotations.append(XSAnnotation(child))
            element.remove(child) # remove processed child from element

class XSSimpleType(XSAnnotated):
    ''' 
    Simple types are derived by restriction, union or list.
    A simple type can't have any attributes or children.
    '''
    # this is about how to define a simpletype
    # anySimpletype is the ur-type and is used to reference any simpletype
    
    def __init__(self, element, xsd):
        '''
        parse the <simpletype> element and store all relevant information.
        '''
        super(XSSimpleType, self).__init__(element, xsd)
        self.content = None
        for child in element.getchildren():
            if child.tag in self.allowed_content:
                self.content = self.allowed_content[child.tag](child, xsd)
            elif child.tag in self.ignored_content:
                continue
            else:
                log.warn("XSSimpleType : Schemaelement " + child.tag + 
                              " not implemented")
            
    def getelement(self):
        '''
        return xsd-element defined for this instance.
        '''
        return self.content.getelement()
    
    def getattributes(self):
        '''
        return xsd-attributes defined for this instance.
        '''
        return None
    
    def gettypename(self):
        '''
        return tuple of nsurl and local name for this type.
        '''
        return self.xsd.targetnamespace, self._name
    
    def getsubelementnames(self, visited=None):
        '''
        return all possible child element names
        '''
        # TODO: can I stop the getParamNames recursion here?
        #       simple types should not allow any childs, so there can't be 
        #       any sub elements. 
        #       but i keep this for attributes
        return self.content.getsubelementnames(visited)
    
    def gettype(self):
        '''
        return xsd-type for this type.
        '''
        return self
    
    def encode(self, data):
        '''
        serialize python data to xml-string.
        '''
        return self.content.encode(data)

    def decode(self, data):
        '''
        deserialize data to python data type.
        '''
        return self.content.decode(data)

class XSRestriction(XSAnnotated):
    '''
    the xsd <restriction> element.
    '''
    # TODO: if a restriction has no content. does it have all content of it's 
    #       base ?
    #       or does a restriction always have to repreat the full content of 
    #       its base?
    # TODO: if a restriction does not have a base attribute it restricts its 
    #       embeddedtype:
    #       e.g.: <restriction><simpleType>....</simpleType></restriction> .. 
    #       but is this allowed?

    def __init__(self, element, xsd):
        '''
        parse all relevant information from the restriction element.
        '''
        super(XSRestriction, self).__init__(element, xsd)
        self.base = qname2clark(element.get("base"), element.nsmap)
        self.content = None
        self.attributes = None
        for child in element.getchildren():
            if child.tag in self.allowed_content:
                self.content = self.allowed_content[child.tag](child, xsd)
            elif child.tag in self.ignored_content:
                continue
            elif child.tag in (clark(NS_XMLSCHEMA, "attribute"), 
                               clark(NS_XMLSCHEMA_99, "attribute")): 
                # I' don't know how to pass atributes
                if not self.attributes:
                    self.attributes = []
                self.attributes.append(XSAttribute(child, xsd))
            elif child.tag in (clark(NS_XMLSCHEMA, "anyAttribute"), 
                               clark(NS_XMLSCHEMA_99, "anyAttribute")):
                pass # ignore anyAttribute for now
                #self.attributes.append(XSAnyAttribute(child))
            elif child.tag in (clark(NS_XMLSCHEMA, "group"), 
                               clark(NS_XMLSCHEMA_99, "group")):
                ref = child.get("ref")
                clarkref = qname2clark(ref, child.nsmap)
                self.content = SchemaReference(clarkref, 'group', xsd)
            else:
                log.warn("XSRestriction : Schemaelement " + child.tag + 
                              " not implemented")
            
    def _getbasecontent(self):
        '''
        helper method to find base type for content.
        '''
        if self.content is None:
            return self.xsd.getType(self.base)
        return self.content
            
    def getelement(self):
        '''
        return xsd-element for this type
        '''
        return self._getbasecontent().getelement()
        
    def getattributes(self):
        '''
        return defined attributes for this type.
        '''
        if self.attributes is None:
            return self.xsd.getType(self.base).getattributes()
        return self.attributes            
        
    def getsubelementnames(self, visited=None):
        '''
        return all possible child element names
        '''
        # TODO: check whether base type can produce parameternames
        return self._getbasecontent().getsubelementnames(visited)
    
    def encode(self, data):
        '''
        serialise with the help of the base type.
        '''
        return self._getbasecontent().encode(data)

    def decode(self, data):
        '''
        deserialise with the help of the base type.
        '''
        return self._getbasecontent().decode(data)

class XSExtension(XSAnnotated):
    '''
    the xsd <extension> element.
    '''
    # TODO: this class needs to be corrected.
    #       an extensions adds something to its base type, so check for base 
    #       content and new content and add up.. the same is valid for 
    #       attributes

    def __init__(self, element, xsd):
        '''
        parse all relevant information from the restriction element.
        '''
        super(XSExtension, self).__init__(element, xsd)
        self.base = qname2clark(element.get("base"), element.nsmap)
        self.extensions = None
        for child in element.getchildren():
            if child.tag in self.allowed_content:
                if not self.extensions:
                    self.extensions = []
                self.extensions.append(self.allowed_content[child.tag](child))
            elif child.tag in self.ignored_content:
                continue
            else:
                log.warn("XSExtension : Schemaelement " + child.tag + 
                              " not implemented")
            
    def getelement(self):
        '''
        return xsd-element for this type
        '''
        return self.xsd.getType(self.base).getelement()
        
    def getsubelementnames(self, visited=None):
        '''
        return all possible child element names
        '''
        # TODO: check whether base type can produce parameternames
        return self.xsd.getType(self.base).getsubelementnames(visited)

class XSChoice(XSAnnotated):
    '''
    the xsd <choice> element.
    '''
    # TODO: there seems to be no difference between choice and sequence?

    def __init__(self, element, xsd):
        '''
        parse all relevant information from the restriction element.
        '''
        super(XSChoice, self).__init__(element, xsd)
        self.content = None
        for child in element.getchildren():
            if child.tag in self.allowed_content:
                if not self.content:
                    self.content = []
                self.content.append(self.allowed_content[child.tag](child, xsd))
            elif child.tag in self.ignored_content:
                continue
            else:
                log.warn("XSChoice : Schemaelement " + child.tag + 
                              " not implemented")
            
    def getelement(self):
        '''
        return xsd-element for all subelements
        '''
        ret = []
        for ctnt in self.content:
            ret.append(ctnt.getelement())
        return ret
    
    def getsubelementnames(self, visited=None):
        '''
        return all possible child element names
        '''
        paramnames = []
        for ctnt in self.content:
            paramnames += ctnt.getsubelementnames(visited)
            #paramnames.append(ctnt.getsubelementnames()) # TODO: use + ?
        return paramnames

class XSSequence(XSAnnotated):
    '''
    the xsd <sequence> element.
    '''

    def __init__(self, element, xsd):
        '''
        parse all relevant information from the restriction element.
        '''
        super(XSSequence, self).__init__(element, xsd)
        self.content = None
        for child in element.getchildren():
            if child.tag in self.allowed_content:
                if not self.content:
                    self.content = []
                self.content.append(self.allowed_content[child.tag](child, xsd))
            elif child.tag in self.ignored_content:
                continue
            else:
                log.warn("XSSequence : Schemaelement " + child.tag + 
                              " not implemented")

    def getelement(self):
        '''
        return xsd-element for all subelements
        '''
        if self.content is None:
            return None
        ret = []
        for ctnt in self.content:
            ret.append(ctnt.getelement())
        return ret
    
    def getsubelementnames(self, visited=None):
        '''
        return all possible child element names
        '''
        if not self.content:
            return None
        paramnames = []
        for ctnt in self.content:
            paramnames += ctnt.getsubelementnames(visited)
        #if len(paramnames) == 1:
        #    paramnames = paramnames[0]
        return paramnames
    
class XSAll(XSAnnotated):
    '''
    the xsd <all> element.
    '''
    
    def __init__(self, element, xsd):
        '''
        parse all relevant information from the restriction element.
        '''
        super(XSAll, self).__init__(element, xsd)
        self.content = None
        for child in element.getchildren():
            childns, childname = clark2tuple(child.tag)
            if childns in (NS_XMLSCHEMA, NS_XMLSCHEMA_99): 
                if childname == "element":
                    if not self.content:
                        self.content = []
                    self.content.append(XSElement(child, xsd))
                else:
                    log.warn("XSAll : Schemaelement " + child.tag + 
                                  " not implemented")
            else:
                log.warn("XSAll : Schema namespace  " + childns + 
                              " not supported")
            
    def getelement(self):
        '''
        return xsd-element for all subelements
        '''
        ret = []
        for ctnt in self.content:
            ret.append(ctnt.getelement())
        return ret
    
    def getsubelementnames(self, visited=None):
        '''
        return all possible child element names
        '''
        paramnames = []
        for ctnt in self.content:
            paramnames += ctnt.getsubelementnames(visited)
            #params = ctnt.getsubelementnames() # maybe add up paramlists
            #if len(params) == 1:
            #    params = params[0]
            #paramnames.append(params)
        return paramnames
    
class XSAny(XSAnnotated):
    '''
    the xsd <any> element.
    '''
    
    def __init__(self, element, xsd):
        '''
        parse all relevant information from the restriction element.
        '''
        super(XSAny, self).__init__(element, xsd)
        self.minoccurs = multiplicity(element.get("minOccurs"))
        self.maxoccurs = multiplicity(element.get("maxOccurs"))
        self.namespace = element.get("namespace")
        self.processcontents = element.get("processCotnents")
        self.xstype = AnyType("any", xsd)
        self._name = 'any'
        
    def getelement(self):
        '''
        return xsd-element for this element
        '''
        return self
    
    def getsubelementnames(self, visited=None):
        '''
        return all possible child element names
        '''
        return {'any': None}
    
    def gettype(self):
        '''
        return xsd-type for this type.
        '''
        return self.xstype
    
    def getlocalname(self):
        '''
        return always the unqalified element name.
        '''
        return self._name
    
    def getname(self):
        '''
        return un/qualified element name according to element form. 
        '''
        return self._name
        # element any is defined with form="qualified"... but it is actually a
        # placeholder for something
        # else, I'm not sure what to do here.

class XSGroup(XSAnnotated):
    '''
    the xsd <group> element.
    '''

    # TODO: maybe it is a group ref... then if possible return real referenced 
    #       group or modify this here to proxy real group
    def __init__(self, element, xsd):
        '''
        parse all relevant information from the restriction element.
        '''
        super(XSGroup, self).__init__(element, xsd)
        self.name = element.get("name")
        for child in element.getchildren():
            childns, childname = clark2tuple(child.tag)
            if childns in (NS_XMLSCHEMA, NS_XMLSCHEMA_99):
                if childname == "choice":
                    self.content = XSChoice(child, xsd)
                elif childname == "sequence":
                    self.content = XSSequence(child, xsd)
                elif childname == "all":
                    self.content = XSAll(child, xsd)
                else:
                    log.warn("XSGroup : Schemaelement " + child.tag + 
                                  " not implemented")
            else:
                log.warn("XSGroup : Schema namespace " + childns + 
                              " not supported")
            
    def getelement(self):
        '''
        return xsd-element for this element
        '''
        return self.content.getelement()
    
    def getattributes(self):
        '''
        return defined attributes for this type.
        '''
        if self.content is not None:
            if hasattr(self.content, 'getattributes'):
                return self.content.getattributes()
        return None 
    
    def getsubelementnames(self, visited=None):
        '''
        return all possible child element names
        '''
        return self.content.getsubelementnames(visited)

    
class XSComplexContent(XSAnnotated):
    '''
    the xsd <complexcontent> element.
    '''
                
    def __init__(self, element, xsd):
        '''
        parse all relevant information from the restriction element.
        '''
        super(XSComplexContent, self).__init__(element, xsd)
        self.content = None
        for child in element.getchildren():
            childns, childname = clark2tuple(child.tag)
            if childns in (NS_XMLSCHEMA, NS_XMLSCHEMA_99):
                if childname == "restriction":
                    self.content = XSRestriction(child, xsd)
                elif childname == "extension":
                    self.content = XSExtension(child, xsd)
                elif childname == "all":
                    self.content = XSAll(child, xsd)
                else:
                    log.warn("XSComplexContent : Schemaelement " + child.tag + 
                                  " not implemented")
            else:
                log.warn("XSComplexContent : Schema namespace " + childns + 
                              " not supported")
            
    def getelement(self):
        '''
        return xsd-element for this element
        '''
        return self.content.getelement()
    
    def getattributes(self):
        '''
        return defined attributes for this type.
        '''
        if self.content is not None:
            if hasattr(self.content, 'getattributes'):
                return self.content.getattributes()
        return None 
        #self.attributes.getattributes()
    
    def getsubelementnames(self, visited=None):
        '''
        return all possible child element names
        '''
        return self.content.getsubelementnames(visited)
    
class XSComplexType(XSAnnotated):
    ''' 
    A complex content type allows attributes and child elements.
    If it containts simplecontent then no child elements are allowd.
    The default for complex content is to derive from anyType and contain complexcontent.
    So if the child element of complexType is not simpleContent or complexContent it
    defaults to complexContent with base="anyType".
    A content element which does not allow any content, must be a complexcontent with no
    structure defined. (simplecontent allows data content)
    
    @todo: maybe interpret XSComplexType always as XSComplexContent
    '''

    def __init__(self, element, xsd):
        '''
        parse all relevant information from the restriction element.
        '''
        super(XSComplexType, self).__init__(element, xsd)
        self.content = None
        self.attributes = None
        self.base = qname2clark(element.get("base"), element.nsmap) 
        # TODO: is this attribute allowed here?
        for child in element.getchildren():
            if child.tag in self.allowed_content:
                self.content = self.allowed_content[child.tag](child, xsd)
            elif child.tag in self.ignored_content:
                continue
            elif child.tag in (clark(NS_XMLSCHEMA, "attribute"), 
                               clark(NS_XMLSCHEMA_99, "attribute")): 
                if not self.attributes:
                    self.attributes = []
                self.attributes.append(XSAttribute(child, xsd))
            elif child.tag in (clark(NS_XMLSCHEMA, "anyAttribute"), 
                               clark(NS_XMLSCHEMA_99, "anyAttribute")):
                pass # ignore anyAttribute for now
                #self.attributes.append(XSAnyAttribute(child))
            elif child.tag in (clark(NS_XMLSCHEMA, "group"), 
                               clark(NS_XMLSCHEMA_99, "group")):
                ref = child.get("ref")
                clarkref = qname2clark(ref, child.nsmap)
                self.content = SchemaReference(clarkref, 'group', xsd)
            else:
                log.warn("XSComplexType : Schemaelement " + child.tag + 
                              " not implemented")
        
    def getelement(self):
        '''
        return xsd-element for this element
        '''
        if self.content is None:
            return None
        return self.content.getelement()
    
    def getattributes(self):
        '''
        return defined attributes for this type.
        '''
        if self.attributes is None:
            if hasattr(self.content, 'getattributes'):
                return self.content.getattributes()
        return self.attributes
    
    def gettypename(self):
        '''
        return tuple of nsurl and local name for this type.
        '''
        return self.xsd.targetnamespace, self._name
    
    def getsubelementnames(self, visited=None):
        '''
        return all possible child element names
        '''
        if self.content is None:
            return None
        return self.content.getsubelementnames(visited)
    
    def gettype(self):
        '''
        return xsd-type for this type.
        '''
        return self

class XSSimpleContent(XSAnnotated):
    '''
    the xsd <simplecontent> element.
    '''
    
    def __init__(self, element, xsd):
        '''
        parse all relevant information from the restriction element.
        '''
        super(XSSimpleContent, self).__init__(element, xsd)
        self.content = None
        for child in element.getchildren():
            childns, childname = clark2tuple(child.tag)
            if childns in (NS_XMLSCHEMA, NS_XMLSCHEMA_99):
                if childname == "restriction":
                    self.content = XSRestriction(child, xsd)
                elif childname == "extension":
                    self.content = XSExtension(child, xsd)
                else:
                    log.warn("XSSimpleContent : Schemaelement " + child.tag + 
                                  " not implemented")
            else:
                log.warn("XSSimpleContent : Schema namespace " + childns + 
                              " not supported")
            
    def getelement(self):
        '''
        return xsd-element for this element
        '''
        return self.content.getelement()
    
    def getsubelementnames(self, visited=None):
        '''
        return all possible child element names
        '''
        # ok simple content can't have any parameter names....
        # but may be there are some attributes?
        return self.content.getsubelementnames(visited)
    
class SchemaReference(object):
    '''
    this is not a real structural element of XML Schema, but it helps me here
    to late bind schema references.
    '''

    def __init__(self, nameref, what, xsd):
        '''
        @param what: what to reference? a "type", "element" or "group"
        @type what: C{string}
        
        @param xsd: the XMLSchema where this instance is contained in
        @type xsd: L{XMLSchema}
        '''
        self.nameref = nameref
        self.what = what
        self.xsd = xsd
        
    def resolve(self):
        '''
        reslve the actual xsd-isntance referred to by this instance.
        '''
        if self.what == 'type':
            ref = self.xsd.getType(self.nameref)
        elif self.what == 'element':
            ref = self.xsd.getElement(self.nameref)
        elif self.what == 'group':
            ref = self.xsd.getGroup(self.nameref)
        elif self.what == 'attribute':
            ref = self.xsd.getAttribute(self.nameref)
        else:
            raise Exception('unknown reference type:' + self.what)
        return ref
    
    def getelement(self):
        '''
        return xsd-element for this element
        '''
        return self.resolve().getelement()
    
    def getattributes(self):
        '''
        return defined attributes for this type.
        '''
        return self.resolve().getattributes()
    
    def gettype(self):
        '''
        return xsd-type for this type.
        '''
        return self.resolve().gettype()
    
    def gettypename(self):
        '''
        return tuple of nsurl and local name for this type.
        '''
        return self.resolve().gettypename()
    
    def tostring(self, data):
        '''
        return string representation of this instance/reference.
        '''
        return self.resolve().tostring(data)
    
    def getsubelementnames(self, visited=None):
        '''
        return all possible child element names
        '''
        return self.resolve().getsubelementnames(visited)

class XSAttribute(XSAnnotated):
    '''
    the xsd <attribute> element.
    '''
    # TODO: currently not really used. It just indicates, that an attribute 
    #       is defined, but serialisation happens in parent element (but 
    #       should happen here)
    # TODO: attribute can also defined with content inside instead of ref or 
    #       type ref
    
    def __init__(self, element, xsd):
        '''
        parse all relevant information from the restriction element.
        '''
        super(XSAttribute, self).__init__(element, xsd)
        elemattrib = element.attrib
        self._xstype = elemattrib.pop("type", None)
        if self._xstype:
            self._xstype = SchemaReference(qname2clark(self._xstype, 
                                                       element.nsmap), 
                                           'type', xsd)
        self.default = elemattrib.pop("default", None)
        self.fixed = elemattrib.pop("fixed", None)
        #self.tns = element.xpath("string(ancestor::xsd:schema\
        #                          //@targetNamespace)", 
        #                         namespaces = {"xsd": NS_XMLSCHEMA})
        self._tns = xsd.targetnamespace
        self._form = elemattrib.pop("form", None)
        if not self._form:
            # I am not sure, but I think, that attributes, even if they are 
            # defined schema global should use the default settings
            if element.getparent().tag in (clark(NS_XMLSCHEMA, "schema"), 
                                           clark(NS_XMLSCHEMA_99, "schema")):
                self._form = "qualified" # top level attributes need to be 
                #                          qualified.
            else:
                #self.form = element.xpath("string(ancestor::xsd:schema\
                #                           //@attributeFormDefault)", 
                #         namespaces = {"xsd": NS_XMLSCHEMA}) or "unqualified"
                self._form = xsd.attributeformdefault or "unqualified"
        self._ref = elemattrib.pop("ref", None)
        if self._ref:
            self._ref = SchemaReference(qname2clark(self._ref, element.nsmap), 
                                        'attribute', xsd)
        self.use = elemattrib.pop("use", None)
        for child in element.getchildren():
            childns, childname = clark2tuple(child.tag)
            if childns in (NS_XMLSCHEMA, NS_XMLSCHEMA_99):
                if childname == "simpleType":
                    self.xstype = XSSimpleType(child, xsd) # ? more than one 
                    #                                          allowed?
                else:
                    log.warn("XSAttribute : Schemaelement " + child.tag + 
                                  " not implemented")
            else:
                log.warn("XSAttribute : Schema namespace " + childns + 
                              " not supported")
            
    def getname(self):
        '''
        return un/qualified name depending on attribute from.
        '''
        if self._ref:
            return self._ref.resolve().getname()
        if self._form == "qualified":
            return clark(self._tns, self._name)
        elif self._form == "unqualified":
            return self._name
        else:
            raise Exception("attribute from must be qualified or unqualified \
                             (%s)" % (self._form))
        
    def getlocalname(self):
        '''
        return alwaus unqualified name.
        '''
        if self._ref:
            return self._ref.resolve().getlocalname()
        return self._name
            
    def encode(self, data):
        '''
        data should be a dictionary possibly containing a value for this 
        attribute return value or None
        
        @todo: change this method to accept value in data instead of dict
        '''
        if self._ref:
            return self._ref.resolve().encode(data)
        if self.use == 'prohibited':
            return (None, None)
        attrvalue = None
        if self.fixed:
            attrvalue = self.fixed
        elif self._name in data:
            attrvalue = self._xstype.resolve().encode(data[self._name])
        elif self.default:
            attrvalue = self.default
        elif self.use == 'required':
            log.warn('XSAttribute : required attribute ' + self._name + 
                          ' not serialized')
            attrvalue = ""
        return attrvalue
    
    def decode(self, data):
        '''
        deserialize data to python data type.
        '''
        if self._ref:
            return self._ref.resolve().decode(data)
        return self._xstype.resolve().decode(data)
            

class XSElement(XSAnnotated):
    ''' 
    An element is a bit special. It can be an element referece, or just 
    reference a type defnition, or it can have its own complexType included.
    '''
    
    # TODO: maybe it is a group ref... then if possible return real referenced 
    #       group or modify this here to proxy real group
    def __init__(self, element, xsd):
        '''
        parse all relevant information from the restriction element.
        '''
        super(XSElement, self).__init__(element, xsd)
        self.keys = []
        self.minoccurs = multiplicity(element.get("minOccurs"))
        self.maxoccurs = multiplicity(element.get("maxOccurs"))
        self._tns = xsd.targetnamespace
        self._form = element.get("form")
        if not self._form:
            if element.getparent().tag in (clark(NS_XMLSCHEMA, "schema"), 
                                           clark(NS_XMLSCHEMA_99, "schema")):
                self._form = "qualified" # top level elements need to be 
                #                          qualified.
            else:
                #self.form = element.xpath("string(ancestor::xsd:schema\
                #                           //@elementFormDefault)", 
                #          namespaces = {"xsd": NS_XMLSCHEMA}) or "unqualified"
                self._form = xsd.elementformdefault # should be bound later... to make it easier to manipulate
        self._xstype = element.get("type")
        if self._xstype:
            self._xstype = SchemaReference(qname2clark(self._xstype, 
                                                       element.nsmap), 
                                           'type', xsd)
        self.ref = element.get("ref")
        if self.ref:
            self.ref = SchemaReference(qname2clark(self.ref, element.nsmap), 
                                       'element', xsd)
        self.content = None
        for child in element.getchildren():
            childns, childname = clark2tuple(child.tag)
            if childns in (NS_XMLSCHEMA, NS_XMLSCHEMA_99):
                if childname == "complexType":
                    self.content = XSComplexType(child, xsd)
                elif childname == "simpleType":
                    self.content = XSSimpleType(child, xsd)
                elif childname in ["key", "unique"]:
                    pass # ignore key for now
                    #self.keys.append(XSKey(child))
                else:
                    log.warn("XSElement : Schemaelement " + child.tag + 
                                  " not implemented ")
            else:
                log.warn("XSElement : Schema namespace " + childns + 
                              " not supported")
                
    def getname(self):
        '''
        return un/qualified element name according to element form. 
        '''
        if self.ref:
            return self.ref.resolve().getname()
        if self._form == "qualified":
            return clark(self._tns, self._name)
        elif self._form == "unqualified":
            return self._name
        else:
            raise Exception("element form has to be qualified or unqualified \
                             (%s)" % (self._form))
        
    def getlocalname(self):
        '''
        return unqualified name of this attribute.
        '''
        if self.ref:
            return self.ref.resolve().getlocalname()
        return self._name
    
    def getsubelementnames(self, visited=None):
        '''
        all elements represent paramnames....
        '''
        if self.ref:
            return self.ref.getsubelementnames(visited)
        if visited is None:
            visited = set()
        if self in visited:
            return self._name
        visited.add(self)
        paramnames = None
        if self._xstype:
            paramnames =  self._xstype.getsubelementnames(visited)
        if self.content:
            paramnames = self.content.getsubelementnames(visited)
        if self._name:
            visited.remove(self)
            return {self._name: paramnames}
        raise Exception('Should never reach here....')
        #return paramNames
    
    def getelement(self):
        '''
        return xsd-element for this element
        '''
        return self
    
    def gettype(self):
        '''
        return xsd-type for this type.
        '''
        if self.ref:
            return self.ref.gettype()
        if self._xstype:
            return self._xstype.gettype()
        return self.content
    
    def getattributes(self):
        '''
        return defined attributes for this type.
        '''
        if self.ref:
            return self.ref.getattributes()
        if self._xstype:
            return self._xstype.getattributes()
        return self.content.getattributes()

###############################################################################
## all the following elements are currently not used and are unmaintained.
## They are left as example on how to reactivate them.
## Before reactivating them, check for changes in code in other components, so 
## that the reactivated ones play nicely with the whole hierarchy.
###############################################################################

# TODO: where is XSNoneType defined? (standard?)        
#class XSNoneType(object):
#
#    def serialize(self, dict, root):
#        # TODO: check dict against nothin
#        return root
#    
#    def getParamNames(self):
#        return None
        
#class XSAny(object):
#    
#    def __init__(self, element):
#        if element.getchildren():
#            raise Exception("No childs allowed for anu")
            
#class XSUnion(object):
#    
#    def __init__(self, element):
#        self.content = []
#        for child in element.getchildren():
#            if child.tag == clark(NS_XMLSCHEMA, "simpleType"):
#                self.content.append(XSSimpleType(child))
#            else:
#                raise Warning("Schemaelement : " + child.tag + 
#                              " not implemented")
            
#class XSList(object):
#    
#    def __init__(self, element):
#        self.itemType = element.get("itemType") # TODO: maybe Type 
#                                                        directly
#        for child in element.getchildren():
#            if child.tag == clark(NS_XMLSCHEMA, "simpleType"):
#                self.itemType = XSSimpleType(child)
#            else: 
#                raise Warning("Schemaelement : " + child.tag + 
#                              " not implemented")
    
#class XSAnyAttribute(object):
#    
#    def __init__(self, element):
#        # TODO: read attributes
#        self.annotations = []
#        for child in element.getchildren():
#            if child.tag == clark(NS_XMLSCHEMA, "annotation"):
#                self.annotations.append(XSAnnotation(child))
#            else:
#                raise Exception("Schemaelement : " + child.tag + 
#                                " not allowed")
            
#class XSEnumeration(object):
#    
#    def __init__(self, element):
#        self.value = element.get("value")
#        if element.getchildren():
#            raise Exception("No childs for enumeration allowed")
        
#class XSPattern(object):
#    
#    def __init__(self, element):
#        self.value = element.get("value") # TODO: annotations seems to be 
#                                                  allowed
#        self.annotations = []
#        for child in element.getchildren():
#            if child.tag == clark(NS_XMLSCHEMA, "annotation"):
#                self.annotations.append(XSAnnotation(child))
#            else:
#                raise Exception("No childs allowed for pattern")

#class XSMinInclusive(object):
#    
#    def __init__(self, element):
#        if element.getchildren():
#            raise Exception("No childs allowed for minInclusive")

#class XSMaxInclusive(object):
#    
#    def __init__(self, element):
#        if element.getchildren():
#            raise Exception("No childs allowed for maxInclusive")

#class XSMinLength(object):
#    
#    def __init__(self, element):
#        if element.getchildren():
#            raise Exception("No childs allowed for minLength")
        
#class XSFractionDigits(object):
#    
#    def __init__(self, element):
#        if element.getchildren():
#            raise Exception("No childs allowed for fractionDigits")
            
#class XSSelector(object):
#    
#    def __init__(self, element):
#        self.xpath = element.get("xpath")
#        if element.getchildren():
#            raise Exception("No child elements allowed here")
        
#class XSField(object):
#
#    def __init__(self, element):
#        self.xpath = element.get("xpath")
#        if element.getchildren():
#            raise Exception("No child elements allowed here")
 
#class XSKey(object):
#    
#    def __init__(self, element):
#        self.name = element.get("name")
#        for child in element.getchildren():
#            if child.tag == clark(NS_XMLSCHEMA, "selector"):
#                self.selector = XSSelector(child)
#            elif child.tag == clark(NS_XMLSCHEMA, "field"):
#                self.field = XSField(child)
#            else:
#                raise Exception(child.tag + " not allowd here")

#class XSAttributeGroup(object):
#    
#    def __init__(self, element):
#        self.name = element.get("name")
#        self.annotations = []
#        self.content = []
#        for child in element.getchildren():
#            if child.tag == clark(NS_XMLSCHEMA, "annotation"):
#                self.annotations.append(XSAnnotation(child))
#            elif child.tag == clark(NS_XMLSCHEMA, "attribute"):
#                self.content.append(XSAttribute(child))
#            else:
#                raise Warning("Schemalement " + child.tag + " not implemented")
            
#class XSNotation(object):
#    
#    def __init__(self, element):
#        if element.getchildren():
#            raise Exception("No childs allowed for notation")

###############################################################################
# class variables fo structural elements are defined here.
# the commented parts are here for informative reasons and maybe to reduce the
# typing effort when reactiviating them
###############################################################################

# I have to define this class variables here, because the values are not defined 
# earlier
XSAnnotation.allowed_content = {clark(NS_XMLSCHEMA, "documentation"): XSDocumentation,
                                clark(NS_XMLSCHEMA_99, "documentation"): XSDocumentation, }
XSAnnotation.ignore_content = [clark(NS_XMLSCHEMA, "appinfo"),
                               clark(NS_XMLSCHEMA_99, "appinfo") ]

XSSimpleType.allowed_content = {clark(NS_XMLSCHEMA, "restriction") : XSRestriction,
                                #clark(NS_XMLSCHEMA, "union"): XSUnion,
                                #clark(NS_XMLSCHEMA, "list"): XSList 
                                clark(NS_XMLSCHEMA_99, "restriction") : XSRestriction,
                                }
# union and list does nothing specail for now. when they are completely implemented,
# then they will choose how to serialize content
XSSimpleType.ignored_content = [clark(NS_XMLSCHEMA, "union"), 
                                clark(NS_XMLSCHEMA, "list"),
                                clark(NS_XMLSCHEMA_99, "union"), 
                                clark(NS_XMLSCHEMA_99, "list")]

XSRestriction.allowed_content = {clark(NS_XMLSCHEMA, "sequence"): XSSequence, 
                                 clark(NS_XMLSCHEMA_99, "sequence"): XSSequence,
                                 clark(NS_XMLSCHEMA, "all"): XSAll, 
                                 clark(NS_XMLSCHEMA_99, "all"): XSAll,
                                 clark(NS_XMLSCHEMA, "choice"): XSChoice, 
                                 clark(NS_XMLSCHEMA_99, "choice"): XSChoice,
                                 # the following are supported, but need special handling
                                 #clark(NS_XMLSCHEMA, "group"): XSGroup, 
                                 #clark(NS_XMLSCHEMA_99, "group"): XSGroup, # only group references make sense here
                                 #clark(NS_XMLSCHEMA, "attribute"): XSAttribute, 
                                 #clark(NS_XMLSCHEMA_99, "attribute"): XSAttribute, 
                                 #clark(NS_XMLSCHEMA, "anyAttribute"): XSAttribute, 
                                 #clark(NS_XMLSCHEMA_99, "anyAttribute"): XSAttribute, 
                                 } 
XSRestriction.ignored_content = [ clark(NS_XMLSCHEMA, x) for x in 
                          ["enumeration", "pattern", 
                           "whiteSpace", "minLength", "simpleType",
                           "fractionDigits", "maxInclusive", 
                           "minInclusive"]] + \
                           [clark(NS_XMLSCHEMA_99, x) for x in 
                          ["enumeration", "pattern", 
                           "whiteSpace", "minLength", "simpleType",
                           "fractionDigits", "maxInclusive", "minInclusive"]]
XSExtension.allowed_content = [] # ignore all content for now
XSExtension.ignored_content = [ clark(NS_XMLSCHEMA, x) for x in 
                          ["sequence", "attribute", "attributeGroup", "group",
                           "choice", "anyAttribute"]] + \
                           [clark(NS_XMLSCHEMA_99, x) for x in 
                          ["sequence", "attribute", "attributeGroup", "group",
                           "choice", "anyAttribute"] ]
XSChoice.allowed_content = {clark(NS_XMLSCHEMA, "element"): XSElement,
                            clark(NS_XMLSCHEMA, "choice"): XSChoice,
                            clark(NS_XMLSCHEMA, "sequence"): XSSequence,
                            clark(NS_XMLSCHEMA_99, "element"): XSElement,
                            clark(NS_XMLSCHEMA_99, "choice"): XSChoice,
                            clark(NS_XMLSCHEMA_99, "sequence"): XSSequence }
XSChoice.ignored_content = [clark(NS_XMLSCHEMA, "group"),
                            clark(NS_XMLSCHEMA_99, "group")]
XSSequence.allowed_content = {clark(NS_XMLSCHEMA, "element"): XSElement, 
                              clark(NS_XMLSCHEMA_99, "element"): XSElement,
                              clark(NS_XMLSCHEMA, "choice"): XSChoice, 
                              clark(NS_XMLSCHEMA_99, "choice"): XSChoice,
                              clark(NS_XMLSCHEMA, "sequence"): XSSequence, 
                              clark(NS_XMLSCHEMA_99, "sequence"): XSSequence,
                              clark(NS_XMLSCHEMA, "any"): XSAny, 
                              clark(NS_XMLSCHEMA_99, "any"): XSAny }
XSSequence.ignored_content = [clark(NS_XMLSCHEMA, "group"), 
                              clark(NS_XMLSCHEMA_99, "group") ] 
XSComplexType.allowed_content = {clark(NS_XMLSCHEMA, "sequence"): XSSequence, 
                                 clark(NS_XMLSCHEMA_99, "sequence"): XSSequence,
                                 clark(NS_XMLSCHEMA, "all"): XSAll, 
                                 clark(NS_XMLSCHEMA_99, "all"): XSAll,
                                 clark(NS_XMLSCHEMA, "choice"): XSChoice, 
                                 clark(NS_XMLSCHEMA_99, "choice"): XSChoice,
                                 clark(NS_XMLSCHEMA, "simpleContent"): XSSimpleContent,
                                 clark(NS_XMLSCHEMA_99, "simpleContent"): XSSimpleContent,
                                 clark(NS_XMLSCHEMA, "complexContent"): XSComplexContent,
                                 clark(NS_XMLSCHEMA_99, "complexContent"): XSComplexContent,
                                 #clark(NS_XMLSCHEMA, "group"): XSGroup, 
                                 #clark(NS_XMLSCHEMA_99, "group"): XSGroup, 
                                 # only group references make sense here
                                 }
XSComplexType.ignored_content = [clark(NS_XMLSCHEMA, "attributeGroup"),
                                 clark(NS_XMLSCHEMA_99, "attributeGroup")  ]
