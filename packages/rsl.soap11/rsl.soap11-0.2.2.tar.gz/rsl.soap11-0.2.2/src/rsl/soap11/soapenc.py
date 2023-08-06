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
This module provides factories for bundled standard soap specific schemas
and provides instances for SOAP-Serialisers.
'''
from pkg_resources import resource_stream
from lxml import etree
from zope.interface import classProvides, directlyProvides

from rsl.interfaces import ISchemaFactory
from rsl.misc.namespace import clark, qname2clark, url2ns
from rsl.xsd.deserialtypes import List, Dict
from rsl.xsd.urtype import AnySimpleType, AnyType
from rsl.xsd.component import XSElement, XSAny, XSSimpleType
from rsl.xsd.namespace import NS_XMLSCHEMA_INSTANCE, NS_XMLSCHEMA
from rsl.xsd.interfaces import IXMLSerializer, IXMLDeserializer
from rsl.xsd.schema import XMLSchema
from rsl.soap11.namespace import NS_SOAPENC
        
def createsoapencschema(schemaparent):
    '''
    factory for bundled soapenc schema.
    '''
    xmlschema = resource_stream(__name__, 'xsds/soapenc.xsd')
    tree = etree.parse(xmlschema)
    schema = XMLSchema(schemaparent)
    schema.frometree(tree.getroot())
    #arrayType = tree.find('{%s}attribute[@name="arrayType"]' % (NS_XMLSCHEMA))
    #schema.attributes['arrayType'] = SoapEncArrayType(arrayType, schema)
    return schema
directlyProvides(createsoapencschema, ISchemaFactory)

def createsoapenvschema(schemaparent):
    '''
    factory for bundled soapenv schema
    '''
    xmlschema = resource_stream(__name__, 'xsds/soapenv.xsd')
    tree = etree.parse(xmlschema)
    schema = XMLSchema(schemaparent)
    schema.frometree(tree.getroot())
    return schema
directlyProvides(createsoapenvschema, ISchemaFactory)

def createsoapschema(schemaparent):
    '''
    factory for bundled soap-wsdl extension schema.
    '''
    xmlschema = resource_stream(__name__, 'xsds/wsdlsoap.xsd')
    tree = etree.parse(xmlschema)
    schema = XMLSchema(schemaparent)
    schema.frometree(tree.getroot())
    return schema
directlyProvides(createsoapschema, ISchemaFactory)

class SoapEncElementSerializer(object):
    '''
    Implementation for soap encoded de/serialiser which uses an element
    name as starting point.
    
    This class just wraps SoapEncSerializer to adapt to IXML(de)Serialiser
    interface.
    '''
    
    classProvides(IXMLSerializer, IXMLDeserializer)
    
    @classmethod
    def serialize(cls, params, typename, schema, root):
        '''
        params ... data structure to serialize
        typename ... element name in typesystem
        schema ... ISchema
        root ... serialize to
        
        return newly created element
        '''
        eltype = schema.getElement(typename)
        if root is None:
            root = etree.Element(eltype.getname())
        else:
            root = etree.SubElement(root, eltype.getname())
        xstype = eltype.gettype()
        return SoapEncSerializer.serialize(params, xstype, schema, root)
    
    @classmethod
    def deserialize(cls, root, typename, schema):
        '''
        convert soap encoded message into python data structure.
        '''
        xstype = schema.getElement(typename).gettype()
        return SoapEncSerializer.deserialize(root, xstype, schema)

    
class SoapEncTypeSerializer(object):
    '''
    Implementation for soap encoded de/serialiser which uses an type
    name as starting point.
    
    This class just wraps SoapEncSerializer to adapt to IXML(de)Serialiser
    interface.
    '''
    
    classProvides(IXMLSerializer, IXMLDeserializer)
    
    @classmethod
    def serialize(cls, params, typename, schema, root):
        '''
        params ... data structure to serialize
        typename ... type name in typesystem
        schema ... ISchema
        root ... serialize to
        
        return newly created element
        '''
        xstype = schema.getType(typename)
        return SoapEncSerializer.serialize(params, xstype, schema, root)
    
    @classmethod
    def deserialize(cls, root, typename, xsd):
        '''
        convert soap encoded message into python data structure.
        '''
        xstype = xsd.getType(typename)
        return SoapEncSerializer.deserialize(root, xstype, xsd)

        
class SoapEncSerializer(object):
    '''
    Implementation for soap encoded de/serialiser.
    '''
    
    # mapping of python data types to predefined xsd and soapenc data types.
    rpc_type_map = {str : (NS_XMLSCHEMA, 'string'),
                unicode: (NS_XMLSCHEMA, 'string'),
                int: (NS_XMLSCHEMA, 'integer'),
                float: (NS_XMLSCHEMA, 'float'),
                list: (NS_SOAPENC, 'Array'),
                tuple: (NS_SOAPENC, 'Array'),
                dict: (NS_SOAPENC, 'Struct'),
                #datetime: clark(NS_SOAPENC, 'dateTime')  
                }

    @classmethod
    def getxsdtype(cls, data):
        '''
        resolve python data type to xsd data typename
        '''
        xsdt = type(data)
        if xsdt in cls.rpc_type_map:
            return cls.rpc_type_map[type(data)]
        return (None, None)
        
    @classmethod
    def addnamespace(cls, nsurl, elem):
        '''
        helper method to add a new namespace definition to the etree
        data structure.
        '''
        oldtag = elem.tag
        elem.tag = clark(nsurl, 'newname')
        elem.tag = oldtag
    
    @classmethod
    def getqname(cls, nsurl, name, elem):
        '''
        get qualified name for namespaceurl and localname.
        if necessary the required namespace definition is added to the etree
        first.
        '''
        try:
            xns = url2ns(nsurl, elem.nsmap)
        except KeyError:
            cls.addnamespace(nsurl, elem)
            xns = url2ns(nsurl, elem.nsmap)
        return '%s:%s' % (xns, name)
    
    @classmethod
    def serialize(cls, params, xstype, types, root):
        '''
        interface adaption to rpc-encoding serialise method.
        '''
        return cls.rpc_serialize(xstype, params, root, types)
    
    @classmethod
    def deserialize(cls, root, xstype, types):
        '''
        interface adaption to rpc-encoding deserialise method.
        '''
        return cls.rpc_deserialize(xstype, root, types)
    
    @classmethod
    def rpc_serialize(cls, xstype, data, root, xsd):
        '''
        the actual rpc-encoding serialise method.
        '''
        if isinstance(xstype, (AnySimpleType, XSSimpleType)):
            if data is None:
                root.set(clark(NS_XMLSCHEMA_INSTANCE, 'nil'), 'true')
            else:
                root.text = xstype.encode(data) # set xsi:type="xsi:string"
            nsurl, name = xstype.gettypename()
            qtype = cls.getqname(nsurl, name, root)
            root.set(clark(NS_XMLSCHEMA_INSTANCE, 'type'), qtype)
            return
        if isinstance(xstype, XSElement): #ComplexType):
            if xstype.getlocalname() not in data:
                return
            if xstype.maxoccurs != 1:
                eltype = xstype.gettype()
                for item in data[xstype.getlocalname()]:
                    elem = etree.SubElement(root, xstype.getname())
                    cls.rpc_serialize(eltype, item, elem, xsd)
            else:
                eltype = xstype.gettype()
                elem = etree.SubElement(root, xstype.getname())
                cls.rpc_serialize(eltype, data[xstype.getlocalname()], 
                                  elem, xsd)
            return
        if isinstance(xstype, XSAny):
            # TODO: maybe if item is a dict, then use item name to serialise 
            #       elements or use soapenc:type elements
            if xstype.getlocalname() not in data:
                #ok here is the point to check for dicts
                if isinstance(data, dict):
                    #then serialize all element of dict
                    for key, val in data.items():
                        elem = etree.SubElement(root, key)
                        if val is None:
                            elem.set(clark(NS_XMLSCHEMA_INSTANCE, "nil"), 
                                     "true")
                        else:
                            nsurl, name = cls.getxsdtype(val)
                            qtype = cls.getqname(nsurl, name, root)
                            elem.set(clark(NS_XMLSCHEMA_INSTANCE, 'type'), 
                                     qtype)
                            xsitype = xsd.getType(clark(nsurl, name))
                            cls.rpc_serialize(xsitype, val, elem, xsd)
                            #elem.text = str(item)
                return
            if xstype.maxoccurs != 1:
                for item in data[xstype.getlocalname()]:
                    try:
                        elem = etree.XML(item)
                    except:
                        elem = etree.SubElement(root, xstype.getname())
                        if item is None:
                            elem.set(clark(NS_XMLSCHEMA_INSTANCE, "nil"), 
                                     "true")
                        else:
                            nsurl, name = cls.getxsdtype(item)
                            qtype = cls.getqname(nsurl, name, root)
                            elem.set(clark(NS_XMLSCHEMA_INSTANCE, 'type'), 
                                     qtype)
                            xsitype = xsd.getType(clark(nsurl, name))
                            cls.rpc_serialize(xsitype, item, elem, xsd)
                            #elem.text = str(item)
                    root.append(elem)
            else:
                try:
                    elem = etree.XML(data[xstype.getlocalname()])
                except:
                    elem = etree.SubElement(root, xstype.getname())
                    if data is None:
                        elem.set(clark(NS_XMLSCHEMA_INSTANCE, "nil"), "true")
                    else:
                        nsurl, name = cls.getxsdtype(data[xstype.getlocalname()])
                        qtype = cls.getqname(nsurl, name, root)
                        elem.set(clark(NS_XMLSCHEMA_INSTANCE, 'type'), qtype)
                        xsitype = xsd.getType(clark(nsurl, name))
                        cls.rpc_serialize(xsitype, data[xstype.getlocalname()],
                                          elem, xsd)
                        #elem.text = str(data[xstype.getLocalName()])
            return
        nsurl, name = xstype.gettypename()
        qtype = cls.getqname(nsurl, name, root)
        root.set(clark(NS_XMLSCHEMA_INSTANCE, 'type'), qtype)
        nexttype = xstype.getelement()
        if nexttype is None:
            return
        if isinstance(nexttype, list):
            for rectype in nexttype:
                cls.rpc_serialize(rectype, data, root, xsd)
        else:
            cls.rpc_serialize(nexttype, data, root, xsd)
        attributes = xstype.getattributes()
        if attributes:
            for attrib in attributes:
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
        helper methods to deserialse xml attributes.
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
    def rpc_deserialize(cls, xstype, root, xsd):
        '''
        the actual rpc-encoding serialise method.
        '''
        # TODO: check for tag name in root... maybe its one of soap-enc:type ...
        # then i would know too, which type it is (in AnyType if)
        if root is None:
            return None
        if 'href' in root.attrib:
            elem = root.getroottree().xpath('//*[@id="%s"]' % 
                                            (root.get("href")[1:]))[0]
            return cls.rpc_deserialize(xstype, elem, xsd)
        if isinstance(xstype, (AnySimpleType, XSSimpleType)):
            return xstype.decode(root.text)
        if isinstance(xstype, AnyType):
            # TODO: Do I really have to care about anytype here? or just 
            #       deserialze XSAny?
            xsitype = root.get(clark(NS_XMLSCHEMA_INSTANCE, 'type'))
            if xsitype is not None:
                xsitype = xsd.getType(qname2clark(xsitype, root.nsmap))
                ret = cls.rpc_deserialize(xsitype, root, xsd)
            else:
                ret = etree.tostring(root)
            return ret
        if isinstance(xstype, XSElement): #ComplexType):
            ret = None
            childname = xstype.getname()
            if xstype.maxoccurs != 1:
                ret = List()
                for childelem in root.findall(childname):
                    xsitype = childelem.get(clark(NS_XMLSCHEMA_INSTANCE,
                                                  'type'))
                    if xsitype is not None:
                        xsitype = xsd.getType(qname2clark(xsitype,
                                                          childelem.nsmap))
                    else:
                        xsitype = xstype.gettype()
                    val = cls.rpc_deserialize(xsitype, childelem, xsd)
                    attr = cls.deserialattributes(xsitype, childelem)
                    if attr:
                        for key, value in attr.items():
                            setattr(val, key, value)
                    ret.append(val)
            else:
                childelem = root.find(childname)
                if childelem is not None:
                    xsitype = childelem.get(clark(NS_XMLSCHEMA_INSTANCE,
                                                  'type'))
                    if xsitype is not None:
                        xsitype = xsd.getType(qname2clark(xsitype,
                                                          childelem.nsmap))
                    else:
                        xsitype = xstype.gettype()
                    val = cls.rpc_deserialize(xsitype, childelem, xsd)
                    attr = cls.deserialattributes(xsitype, childelem)
                    if attr:
                        for key, value in attr.items():
                            setattr(val, key, value)
                    ret = val
            return ret
        if isinstance(xstype, XSAny):
            # TODO: check for multiplicity unbound
            if xstype.maxoccurs != 1:
                ret = List()
                for childelem in root:
                    xsitype = childelem.get(clark(NS_XMLSCHEMA_INSTANCE,
                                                  'type'))
                    if xsitype is not None:
                        xsitype = xsd.getType(qname2clark(xsitype,
                                                          childelem.nsmap))
                    else:
                        # check for elem name
                        try:
                            xsitype = xsd.getType(childelem.tag)
                        except KeyError:
                            xsitype = xstype.gettype()
                    ret.append(cls.rpc_deserialize(xsitype, childelem, xsd))
            else:
                childelem = root[0]
                xsitype = childelem.get(clark(NS_XMLSCHEMA_INSTANCE, 'type'))
                if xsitype is not None:
                    xsitype = xsd.getType(qname2clark(xsitype, childelem.nsmap))
                else:
                    # check for elem name
                    try:
                        xsitype = xsd.getType(childelem.tag)
                    except KeyError:
                        xsitype = xstype.gettype()
                ret = cls.rpc_deserialize(xsitype, childelem, xsd)
            return ret
        nexttype = xstype.getelement()
        if nexttype is None:
            return
        if isinstance(nexttype, list):
            ret = Dict()
            for rectype in nexttype: # TODO: possibly create map here
                ret[rectype.getlocalname()] = cls.rpc_deserialize(rectype,
                                                                  root, xsd)
            if len(nexttype) == 1:
                ret = ret.values()[0]
            return ret
        else:
            return cls.rpc_deserialize(nexttype, root, xsd)
