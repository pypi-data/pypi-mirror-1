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
This module defines the WSDL soap extension elements.
'''
from warnings import warn

from zope.interface import directlyProvides

from rsl.implementations import ParamInfo
from rsl.wsdl1.interfaces import IWSDLExtensionFactory
from rsl.wsdl1.binding import WSDLPort, WSDLBinding, WSDLOperation
from rsl.wsdl1.binding import WSDLParamInfo, WSDLFault
from rsl.soap11.namespace import NS_SOAP
from rsl.misc.namespace import clark, clark2tuple, qname2clark

class SOAPPort(WSDLPort):
    '''
    The soap port element extension.
    '''
    
    def __init__(self, wsdl):
        '''
        initialise empty element.
        '''
        super(SOAPPort, self).__init__(wsdl)
        self.location = None
        self.namespace = None
        
    def frometree(self, etree):
        '''
        parse soap:address element.
        '''
        soapportelem = etree.find(clark(NS_SOAP, 'address'))
        self.location = soapportelem.get('location')
        self.namespace = NS_SOAP
        super(SOAPPort, self).frometree(etree)
        return self
    
def soapportfactory(wsdl, portelem):
    '''
    The factory method to create SOAPPort instances.
    '''
    port = SOAPPort(wsdl)
    port = port.frometree(portelem)
    return port
directlyProvides(soapportfactory, IWSDLExtensionFactory)

class SOAPBinding(WSDLBinding):
    '''
    the soap:binding instance.
    '''
    
    def __init__(self, wsdl):
        '''
        initialise empty instance.
        '''
        super(SOAPBinding, self).__init__(wsdl)
        self.style = 'document'
        self.transport = None
    
    def frometree(self, etree):
        '''
        parse soap:binding extension.
        '''
        soapbindelem = etree.find(clark(NS_SOAP, 'binding'))
        self.style = soapbindelem.get('style', self.style)
        self.transport = soapbindelem.get('transport')
        super(SOAPBinding, self).frometree(etree)
        return self

def soapbindingfactory(wsdl, bindingelem):
    '''
    The factory method to create SOAPBinding instances.
    '''
    binding = SOAPBinding(wsdl)
    binding = binding.frometree(bindingelem)
    return binding
directlyProvides(soapbindingfactory, IWSDLExtensionFactory)

class SOAPOperation(WSDLOperation):
    '''
    the soap:operation extension element.
    '''
    
    def __init__(self, binding):
        '''
        initialise empty instance.
        '''
        super(SOAPOperation, self).__init__(binding)
        self.soapaction = None
        self.style = binding.style
        
    def frometree(self, opelem):
        '''
        parse soap:operation extension element.
        '''
        super(SOAPOperation, self).frometree(opelem)
        soapopelem = opelem.find(clark(NS_SOAP, 'operation'))
        self.soapaction = soapopelem.get('soapAction')
        self.style = soapopelem.get('style', self.style)
        return self
    
    def getOperationInfo(self):
        '''
        add additional information to IOperationInfo created by base class.
        '''
        opinfo = super(SOAPOperation, self).getOperationInfo()
        # extended elements
        opinfo.soapaction = self.soapaction
        opinfo.style = self.style
        opinfo.transport = self.binding.transport
        return opinfo

def soapoperationfactory(binding, operationelem):
    '''
    Factory method to create SOAPOperation instances.
    '''
    operation = SOAPOperation(binding)
    operation = operation.frometree(operationelem)
    return operation
directlyProvides(soapoperationfactory, IWSDLExtensionFactory)

    
class SOAPParamInfo(WSDLParamInfo):
    '''
    extend WSDL specific I/O parameter infos with soap specific information.
    '''
    
    def __init__(self, operation):
        '''
        initialise empty instance.
        '''
        super(SOAPParamInfo, self).__init__(operation)
        self.body = None
        self.headers = None
    
    def frometree(self, inputelem):
        '''
        parse information about I/O parameters from etree instance. 
        ''' 
        # inputelem can also be an outputelem
        super(SOAPParamInfo, self).frometree(inputelem)
        for child in inputelem:
            _, name = clark2tuple(child.tag)
            if name == 'body':
                self.body = {}
                self.body['parts'] = child.get('parts')
                if self.body['parts'] is not None:
                    self.body['parts'] = self.body['parts'].split()
                self.body['use'] = child.get('use', 'literal')
                self.body['encodingStyle'] = child.get('encodingStyle')
                self.body['namespace'] = child.get('namespace')
            elif name == 'header':
                header = {}
                header['message'] = qname2clark(child.get('message'), 
                                                child.nsmap)
                header['part'] = child.get('part')
                header['use'] = child.get('use', 'literal')
                header['encodingStyle'] = child.get('encodingStyle')
                header['namespace'] = child.get('namespace')
                if self.headers is None:
                    self.headers = []
                self.headers.append(header)
            else:
                warn("Unknown element '%s' in binding/operation/input" %
                     child.tag)
        return self
    
    def getSerializer(self):
        '''
        return name of serializer for soap1.1
        '''
        return 'soap:envelope:1.1'
    
    def getParamInfo(self):
        '''
        return IParamInfo instance filled with information from this instance.
        
        This method does not really comply to standard interface because of
        special soap handling. It returns a dictionary.
        {'wrapper' ... the wrapper element if any
         'body' .... a list of body IParamInfo
         'header' ... a list of header IParamInfo
        }
        this return value can only be used in conjunction with an 
        soap-envelope-serialiser
        
        @todo: can I return just self?
        '''
        # for each param (body + header)
        # create a ParamInfo object ['name', 'xs:type', 'serializer', 
        # 'hedaer|body'
        #
        # return dict: {'wrapper', 'body', 'header'}
        #
        # find message definition:
        porttype = self.operation.binding.wsdl.porttypes[self.operation.binding.porttype]
        porttypeoperation = porttype[self.operation.name]
        message = self.operation.binding.wsdl.messages[porttypeoperation[self.tag]['message']]
        msgparts = message[:]
        if self.body and (self.body['parts'] is not None):
            # or only those parts lists in parts attribute
            msgparts = [p for p in msgparts if p['name'] in self.body['parts']]
        ret = {}
        ret['body'] = params = []
        if self.operation.style == 'rpc':
            ret['wrapper'] = wrapper = {}
            wrapper['namespace'] = self.body['namespace']
            wrapper['name'] = self.operation.name
            for part in msgparts:
                param = ParamInfo()
                # part can contain an element or a type
                # if element: the element name is used else the part name
                if 'type' in part:
                    param.name = part['name']
                    param.type = part['type']
                    param.serializer = 'soap:rpc:' + self.body['use'] + ':type'
                    # namespace?
                    param.namespace = None
                else:
                    param.namespace, param.name = clark2tuple(part['element'])
                    param.type = part['element'] 
                    param.serializer = 'soap:rpc:' + self.body['use'] + \
                                       ':element'
                params.append(param)
        elif self.operation.style == 'document':
            # TODO: add possibility for user to avoid unwrapping
            if (len(msgparts) == 1) and ('element' in msgparts[0]):
                # possible wrapped style
                # check if element has sub elements
                eltype = self.operation.binding.wsdl.types.getElement(msgparts[0]['element'])
                subparts = eltype.gettype().getelement()
                if subparts is None or isinstance(subparts, list):
                    # subparts is None: doc/lit/wrap for empty param set
                    # subparts is List: doc/lit/wrap for numerous params
                    # subparts is not List: we can't wrap this, else we have
                    #          no param name
                    # ok we can unwrap... let's do it
                    wrapper = ret['wrapper'] = {}
                    wrapper['namespace'], wrapper['name'] = clark2tuple(msgparts[0]['element'])
                    wrapper['type'] = eltype.getname()
                    wrapper['serializer'] = 'soap:document:' + \
                                            self.body['use'] + ':element'
                    if subparts is not None:
                        for part in subparts:
                            # TODO: this here can be non referenceable elements
                            param = ParamInfo()
                            _, param.name = clark2tuple(part.getname())
                            param.type = part.getname()
                            param.serializer = 'soap:document:' + \
                                               self.body['use'] + ':element'
                            params.append(param)
            # do the unwrapped thing:
            if 'wrapper' not in ret:
                for part in msgparts:
                    param = ParamInfo()
                    if 'type' in part:
                        param.name = part['name']
                        param.type = part['type']
                        params.serializer = 'soap:document:' + \
                                            self.body['use'] + ':type'
                        param.namespace = None
                    else:
                        param.namespace, param.name = clark2tuple(part['element'])
                        param.type = part['element']
                        param.serializer = 'soap:document:' + \
                                           self.body['use'] + ':element'
                    params.append(param)
        else:
            raise Exception('Unknown operation style "%s".' % 
                            self.operation.style)
        # ok ... body parts are finished... let's go for header parts
        if self.headers is not None:
            headerparams = ret['header'] = []
            for header in self.headers:
                # get corresponding msgpart
                message = self.operation.binding.wsdl.messages[header['message']]
                part = None
                for mpart in message:
                    if mpart['name'] == header['part']:
                        part = mpart
                        break
                param = ParamInfo()
                if 'type' in part:
                    param.name = part['name']
                    param.type = part['type']
                    param.serializer = 'soap:' + self.operation.style + ':' + \
                                       self.body['use'] + ':type'
                    param.namespace = None
                else:
                    param.namespace, param.name = clark2tuple(part['element'])
                    param.type = part['element']
                    param.serializer = 'soap:' + self.operation.style + ':' + \
                                       self.body['use'] + ':element'
                # TODO: spec says that for headers document style is assumed, 
                #       because headers do not make sense for rpc style.
                #       does this mean, that headers never can be in rpc style?
                # TODO: missing encodingStyles
                headerparams.append(param)        
        return ret
    
def soapparaminfofactory(operation, inputelem):
    '''
    Factory for SOAPParamInfo instances.
    '''
    paraminfo = SOAPParamInfo(operation)
    paraminfo = paraminfo.frometree(inputelem)
    return paraminfo
directlyProvides(soapparaminfofactory, IWSDLExtensionFactory)
        
class SOAPFault(WSDLFault):
    '''
    the soap:fault extension element.
    '''
    
    def __init__(self, operation):
        '''
        init empty instance.
        '''
        super(SOAPFault, self).__init__(operation)
        self.encodingstyle = None
        self.use = None
        self.namespace = None
        
    def frometree(self, faultelem):
        '''
        parse soap:fault extension element.
        '''
        super(SOAPFault, self).frometree(faultelem)
        soapfaultelem = faultelem.find(clark(NS_SOAP, 'fault'))
        self.encodingstyle = soapfaultelem.get('encodingStyle')
        self.use = soapfaultelem.get('use')
        self.namespace = soapfaultelem.get('namespace')
        return self

def soapfaultfactory(operation, faultelem):
    '''
    Factory function to create SOAPFault instances.
    '''
    fault = SOAPFault(operation)
    fault = fault.frometree(faultelem)
    return fault
directlyProvides(soapfaultfactory, IWSDLExtensionFactory)
