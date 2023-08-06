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
This module provides the IProxy implementation for SOAP 1.1
'''
from zope.interface import implements, classProvides

from rsl.globalregistry import lookupimpl
from rsl.interfaces import ITransport, IProxyFactory, IProxy, ISerializer
from rsl.interfaces import IDeserializer
from rsl.soap11.namespace import NS_SOAP

class SOAPProxy(object):
    '''
    The IProxy implementation.
    '''
    
    implements(IProxy)
    classProvides(IProxyFactory)
    
    ptype = NS_SOAP
    
    def __init__(self, location, name=None):
        '''
        initialise empty proxy.
        '''
        super(SOAPProxy, self).__init__()
        self.callables = {}
        self.location = location
        self.name = name
        
    def __getattr__(self, name):
        '''
        allow method access as object attributes.
        '''
        if name in self.callables:
            return self.callables[name]
        raise AttributeError
    
    def callRemote(self, name, *args, **kws):
        '''
        call remote method.
        '''
        self.__getattr__(name)(*args, **kws)
        
    def addOperation(self, name, operationinfo):
        '''
        add method definition to this proxy. all necessary information
        is passed as IOperationInfo instance.
        '''
        #operation: name, soapaction, style,
        #           input, output, faults
        func = Callable(self.location, operationinfo)
        self.callables[func.name] = func


class Callable(object):
    ''' 
    a callable needs to know the endpoint (port)
    the transport (binding)
    and the encoding (operation)
    
    To modify the transport, just extend the transportfactory
    or set a specific transport directly on the binding
    '''
    def __init__(self, url, operationinfo):
        '''
        initialise callable from IOperationInfo.
        '''
        self.url = url
        self.name = operationinfo.name
        self.operationinfo = operationinfo
        self.transport = operationinfo.transport
        self.paramnames = [bpar.name for bpar in operationinfo.input['body']]
        if 'header' in operationinfo.input:
            self.paramnames += [hpar.name for hpar in 
                                operationinfo.input['header']] 
        
    def __call__(self, *args, **kws):
        ''' 
        _headers, _attrs 
        
        do serialisation, wire transfer, deserialisation.
        '''
        headers, payload = self.serialize(*args, **kws)
        headers, response = self.send(payload, headers)
        # TODO: various unpack options
        return self.deserialize(headers, response)

        
    def serialize(self, *args, **kws):
        '''
        serialise all given parameters into SOAP-Envelope.
        '''
        # prepare params
        params = {} 
        if self.paramnames:
            pnames = self.paramnames[:]
            for arg in args:
                if pnames:
                    params[pnames.pop(0)] = arg
        # TODO: kw-param could overwrite non-kw param...
        params.update(kws)
        # we need to create an envelope....
        serialiser = lookupimpl(ISerializer, self.operationinfo.serializer)
        headers, payload = serialiser.serialize(params, self.operationinfo)
        return headers, payload
        
    def deserialize(self, headers, response):
        '''
        deserialise response from remote endpoint.
        '''
        # TODO: maybe deserializer is different from serializer?
        serialiser = lookupimpl(IDeserializer, self.operationinfo.serializer)
        headers, payload = serialiser.deserialize(response, self.operationinfo,
                                                  headers=headers)
        return headers, payload
        
    def send(self, payload, headers):
        '''
        send request and retrieve response.
        '''
        transport = lookupimpl(ITransport, self.transport)
        return transport.send(self.url, payload, headers=headers)
