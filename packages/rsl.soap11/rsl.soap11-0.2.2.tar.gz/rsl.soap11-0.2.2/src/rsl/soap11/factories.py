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
from rsl.globalregistry import registerimpl
from rsl.transport.urllib2transport import Urllib2Transport
from rsl.soap11.namespace import NS_SOAP, NS_SOAPENV, HTTP_TRANSPORT, NS_SOAPENC
from rsl.soap11.serializer import SOAPEnvelopeSerializer
from rsl.soap11.soapenc import createsoapencschema, createsoapenvschema
from rsl.soap11.soapenc import createsoapschema
from rsl.soap11.soapenc import SoapEncElementSerializer, SoapEncTypeSerializer
from rsl.soap11.proxy import SOAPProxy
from rsl.xsd.interfaces import IXMLDeserializer, IXMLSerializer
from rsl.xsd.serializer import XMLElementSerializer, XMLTypeSerializer
from rsl.interfaces import ITransport, IProxyFactory, ISchemaFactory
from rsl.interfaces import ISerializer, IDeserializer

def register():
    registerimpl(ITransport, HTTP_TRANSPORT, Urllib2Transport)
    registerimpl(ISerializer, 'soap:envelope:1.1', SOAPEnvelopeSerializer)
    registerimpl(IDeserializer, 'soap:envelope:1.1', SOAPEnvelopeSerializer)
    # TODO: the next three serialiser do not conform to ISerializer interface
    # (wrong parameter order, and return value is not a tuple) the same for
    # deserialize methods
    
    registerimpl(IXMLSerializer, 'soap:document:literal:element', XMLElementSerializer)
    registerimpl(IXMLDeserializer, 'soap:document:literal:element', XMLElementSerializer)
    registerimpl(IXMLSerializer, 'soap:document:literal:type', XMLTypeSerializer)
    registerimpl(IXMLDeserializer, 'soap:document:literal:type', XMLTypeSerializer)
    
    registerimpl(IXMLSerializer, 'soap:rpc:literal:element', XMLElementSerializer)
    registerimpl(IXMLDeserializer, 'soap:rpc:literal:element', XMLElementSerializer)
    registerimpl(IXMLSerializer, 'soap:rpc:literal:type', XMLTypeSerializer)
    registerimpl(IXMLDeserializer, 'soap:rpc:literal:type', XMLTypeSerializer)
    
    registerimpl(IXMLSerializer, 'soap:rpc:encoded:element', SoapEncElementSerializer)
    registerimpl(IXMLDeserializer, 'soap:rpc:encoded:element', SoapEncElementSerializer)
    registerimpl(IXMLSerializer, 'soap:rpc:encoded:type', SoapEncTypeSerializer)
    registerimpl(IXMLDeserializer, 'soap:rpc:encoded:type', SoapEncTypeSerializer)
    
    registerimpl(ISchemaFactory, NS_SOAPENC, createsoapencschema)
    registerimpl(ISchemaFactory, NS_SOAPENV, createsoapenvschema)
    registerimpl(ISchemaFactory, NS_SOAP, createsoapschema)
    registerimpl(IProxyFactory, NS_SOAP, SOAPProxy)
