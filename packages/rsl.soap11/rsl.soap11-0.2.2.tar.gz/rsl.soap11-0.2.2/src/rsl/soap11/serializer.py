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
This module provides SOAP envelope serialiser. These serialiser mainly create
the SOAP envelope and then use XMLSchema- or XMLSOAPEnc- serialisers to encode
payload.
'''

# NOTES: for namespace usage:
#        the description down here for namespaces assumes 
#           elementFormDefault="unqualified" which is the default in XMLSchema.
#        maybe some of the namespace rules has to be redefined for 
#           elementFormDefault="qualified"
# NOTES: 
# rpc/enc: no namespaces and elements are type with xsi:type
#          part definition contain type information
#          first body element is operation name
#          operation element comes from wsdl further content comes from schema
#          not WS-I compliant but valid
# rplc/lit: no namespaces and elements are normally not typed with xsi:type...
#           xsi:type may be required for polymorphism or if a type is derived 
#           from another part definitions contain type information.
#          first body element is operation name
#          operation element comes from wsdl further content comes from schema
#          namespaces:
#              if operation has namespace: operation mus be qualifed and childs 
#                  are unqalified (no namespace declaration.., empty namespace)
#                  childs from other namespaces than the one overriden by 
#                  operation must be qualified again
#              if operation has no namespace: operation is unqualified (empty 
#                  namespace) and child are qualified according to namespace
# doc/enc: not used
# doc/lit: needs schema definition
#          part definitions contain element reference
#          operation name is not serialized
# doc/lit/wrapped: is just a convention to wrap all parts into one element, 
#                  which is defined by a schema this single element may
#                  represent the method name (but is in principle independent
#                  of method name) and eases to comply with only one child
#                  element in body.
#          namespaces:
#                if operation has namespaces (non WS-I cokmpliance): childs
#                are unqualified else: just use schema namespaces.
# NOTES:
# WS-I allows only one child element in body
# TODO: in serialize with xsi:nil possibilityies check for schema nillable=true
from lxml import etree
from zope.interface import classProvides

from rsl.globalregistry import lookupimpl
from rsl.interfaces import ISerializer, IDeserializer
from rsl.xsd.interfaces import IXMLSerializer, IXMLDeserializer
from rsl.xsd.namespace import NS_XMLSCHEMA, NS_XMLSCHEMA_99
from rsl.xsd.namespace import NS_XMLSCHEMA_INSTANCE
from rsl.misc.namespace import clark
from rsl.soap11.namespace import NS_SOAPENV, NS_SOAPENC
from rsl.soap11.fault import SOAPFault

# 'soap:envelope:1.1'
class SOAPEnvelopeSerializer(object):
    '''
    The SOAP 1.1 envelope serialiser.
    '''

    classProvides(ISerializer, IDeserializer)
    
    @classmethod
    def serialize(cls, params, operationinfo, **kws):
        '''
        params    ... dict of values to serialise
        partsinfo ... partinfos as returned from IParamInfo.getParts()
        types     ... ISchemaCollection
        '''
        # TODO: add the following namespace only if required.
        envelope = etree.Element("{%s}Envelope" % (NS_SOAPENV), 
                                 nsmap={"SOAP-ENV": NS_SOAPENV, 
                                        'xsi': NS_XMLSCHEMA_INSTANCE,
                                        'xsd': NS_XMLSCHEMA,
                                        "SOAP-ENC": NS_SOAPENC,
                                        'xsd99': NS_XMLSCHEMA_99})
        # 1. serialise headers:
        if 'header' in operationinfo.input:
            headerparts = operationinfo.input['header']
            if headerparts:
                header = etree.SubElement(envelope, clark(NS_SOAPENV, "Header"))
            for hps in headerparts:
                serialiser = lookupimpl(IXMLSerializer, hps.serializer)
                serialiser.serialize(params[hps.name], hps.type, 
                                     operationinfo.typesystem, header)
        # 2. serialise body:
        bodyparts = operationinfo.input['body']
        body = etree.SubElement(envelope, clark(NS_SOAPENV, "Body"))
        # Do we use wrapped style or rpc?
        if 'wrapper' in operationinfo.input:
            wrapper = operationinfo.input['wrapper']
            # if wrapper has a 'type' field, then we have doc/lit/wrap
            if 'type' in wrapper:
                #params = {self.input['wrapper']['name'] : params}
                serialiser = lookupimpl(IXMLSerializer, wrapper['serializer'])
                serialiser.serialize(params, wrapper['type'], 
                                     operationinfo.typesystem, body)
            else:
                # TODO: I don't want to do this here, but for now ok.
                root = etree.SubElement(body, clark(wrapper['namespace'], 
                                                    wrapper['name']))
        else:
            root = body
        if not (('wrapper' in operationinfo.input) and 
                ('type' in operationinfo.input['wrapper'])):
            for bps in bodyparts:
                if bps.name in params:
                    # TODO: Bad hack here... if we have a type serializer here,
                    #       we need to create an element before
                    if bps.serializer.endswith(':type'):
                        sroot = etree.SubElement(root, clark(bps.namespace,
                                                             bps.name))
                    else:
                        sroot = root
                    serialiser = lookupimpl(IXMLSerializer, bps.serializer)
                    serialiser.serialize(params[bps.name], bps.type,
                                         operationinfo.typesystem, sroot)
        payload = etree.tostring(envelope, pretty_print=False, encoding='utf-8',
                                 xml_declaration=True) 
        headers = {'Content-Type': 'text/xml; charset=utf-8',
                   'SOAPAction': '"%s"' % operationinfo.soapaction}
        return headers, payload
    
    @classmethod
    def deserialize(cls, response, operationinfo, **kws):
        '''
        headers ... headers from request.
        operationinfo ... IOperationInfo instance
        '''
        # ok here we can do a lot of stuff... like check envelope version, 
        #    encodingStyle, aso....
        #1. get envelope and header/body parts
        try:
            envelope = etree.fromstring(response)
            headerelem = envelope.find(clark(NS_SOAPENV, 'Header'))
            bodyelem = envelope.find(clark(NS_SOAPENV, 'Body'))
            headerret = bodyret = None
            if headerelem is not None and len(headerelem) > 0:
                # TODO: maybe check for more than just the defined header blocks
                # TODO: what about undefined header parts?
                headerparts = operationinfo.output['header']
                for hps in headerparts:
                    partelem = headerelem.find(clark(hps.namespace, hps.name))
                    serialiser = lookupimpl(IXMLDeserializer, hps.serializer)
                    headerval = serialiser.deserialize(partelem, hps.type,
                                                       operationinfo.typesystem)
                    if headerret is None:
                        headerret = {}
                    headerret[hps.name] = headerval
                
            # TODO: to be strict bodyelem must not be None, but can be empty
            if bodyelem is not None and len(bodyelem) > 0:
                fault = bodyelem.find(clark(NS_SOAPENV, 'Fault'))
                if fault is not None:
                    faultcode = bodyelem.find(".//faultcode").text
                    faultstring = bodyelem.find(".//faultstring").text
                    faultactor = bodyelem.find(".//faultactor")
                    if faultactor is not None:
                        faultactor = faultactor.text
                    detailel = bodyelem.find(".//detail")
                    detail = None
                    if detailel is not None:
                        detail = ''
                        for dtl in detailel:
                            detail += etree.tostring(dtl)
                    raise SOAPFault(faultcode, faultstring, faultactor, detail)
                if 'wrapper' in operationinfo.output:
                    # ok we have some wrapped style (rpc or doc/lit/wrap)
                    # just ignore the only child...
                    bodyroot = bodyelem[0]
                    if 'type' in operationinfo.output['wrapper']:
                        # here we have doc/lit/wrapped:
                        wrapper = operationinfo.output['wrapper']
                        serialiser = lookupimpl(IXMLDeserializer, 
                                                wrapper['serializer'])
                        bodyval = serialiser.deserialize(bodyroot, 
                                                    wrapper['type'],
                                                    operationinfo.typesystem)
                        # unwrap return values:
                        # Seems like, deserialiser does this already
                        bodyret = bodyval
                else:
                    bodyroot = bodyelem
                if not (('wrapper' in operationinfo.output) and
                        ('type' in operationinfo.output['wrapper'])):
                    for bps in operationinfo.output['body']:
                        partelem = bodyroot.find(clark(bps.namespace,
                                                       bps.name))
                        serialiser = lookupimpl(IXMLDeserializer,
                                                bps.serializer)
                        bodyval = serialiser.deserialize(partelem, bps.type,
                                                    operationinfo.typesystem)
                        if bodyret is None:
                            bodyret = {}
                            bodyret[bps.name] = bodyval
        except SOAPFault:
            raise
        except Exception, exc:
            #import traceback
            #traceback.print_exc()
            raise SOAPFault('Client', str(exc), 'self', exc)
        return headerret, bodyret
