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
Implementations for the WSDL 1 artifacts which are required for http encoding.
'''

from zope.interface import directlyProvides

from rsl.misc.namespace import clark, clark2tuple
from rsl.wsdl1.binding import WSDLPort, WSDLBinding, WSDLOperation
from rsl.wsdl1.binding import WSDLParamInfo
from rsl.wsdl1.interfaces import IWSDLExtensionFactory
from rsl.http.namespace import NS_HTTP
from rsl.implementations import ParamInfo

class HTTPPort(WSDLPort):
    '''
    WSDL 1 http-port
    '''
    
    def __init__(self, wsdl):
        '''
        initialise empty HTTPPort.
        '''
        super(HTTPPort, self).__init__(wsdl)
        self.location = None
        self.namespace = None
        
    def frometree(self, etree):
        '''
        initialise this instance with data from element-tree.
        '''
        soapportelem = etree.find(clark(NS_HTTP, 'address'))
        self.location = soapportelem.get('location')
        self.namespace = NS_HTTP
        super(HTTPPort, self).frometree(etree)
        return self
    
def httpportfactory(wsdl, portelem):
    '''
    factory method for wsdl-http-port extension element.
    '''
    port = HTTPPort(wsdl)
    port = port.frometree(portelem)
    return port
directlyProvides(httpportfactory, IWSDLExtensionFactory)

class HTTPBinding(WSDLBinding):
    '''
    WSDL 1 http-binding.
    '''
    
    def __init__(self, wsdl):
        '''
        create empty HTTPBinding.
        '''
        super(HTTPBinding, self).__init__(wsdl)
        self.verb = None
        
    def frometree(self, bindingelem):
        '''
        initialise this instance with data from element-tree.
        '''
        httpbindelem = bindingelem.find(clark(NS_HTTP, 'binding'))
        self.verb = httpbindelem.get('verb')
        super(HTTPBinding, self).frometree(bindingelem)
        return self
    
def httpbindingfactory(wsdl, bindingelem):
    '''
    factory method for wsdl-http-binding extension element.
    '''
    binding = HTTPBinding(wsdl)
    binding = binding.frometree(bindingelem)
    return binding
directlyProvides(httpbindingfactory, IWSDLExtensionFactory)
    
class HTTPOperation(WSDLOperation):
    '''
    WSDL 1 http-binding.
    '''
    
    def __init__(self, binding):
        '''
        create empty HTTPOperation.
        '''
        super(HTTPOperation, self).__init__(binding)
        self.location = None
        
    def frometree(self, operationelem):
        '''
        initialise this instance with data from element-tree.
        '''
        httpoperationelem = operationelem.find(clark(NS_HTTP, 'operation'))
        self.location = httpoperationelem.get('location')
        super(HTTPOperation, self).frometree(operationelem)
        return self
    
    def getOperationInfo(self):
        '''
        return IOperationInfo instance filled with information from this
        Operation instance.
        '''
        opinfo = super(HTTPOperation, self).getOperationInfo()
        # extended infos
        opinfo.location = self.location
        opinfo.method = self.binding.verb
        # TODO: where to get verb from? should this passed to proxy or put it here into opinfo
        #       if in opinfo, then it may be necessary to calculate default verb
        return opinfo
    
def httpoperationfactory(binding, operationelem):
    '''
    factory method for wsdl-http-operation extension element.
    '''
    operation = HTTPOperation(binding)
    operation = operation.frometree(operationelem)
    return operation
directlyProvides(httpoperationfactory, IWSDLExtensionFactory)
    
class HTTPParamInfo(WSDLParamInfo):
    '''
    extend WSDL specific I/O parameter infos with wsdl-http specific information.
    '''
    
    def __init__(self, operation):
        '''
        initialise empty instance.
        '''
        super(HTTPParamInfo, self).__init__(operation)
        self.exttag = None
        
    def frometree(self, inputelem): #also used for outputelem
        '''
        parse information about I/O parameters from etree instance. 
        ''' 
        _, self.exttag = clark2tuple(inputelem[0].tag)
        super(HTTPParamInfo, self).frometree(inputelem)
        return self
    
    def getSerializer(self):
        '''
        return name of serializer for wsdl 1 - http binding.
        '''
        if self.exttag == 'urlEncoded':
            return 'application/x-www-form-urlencoded'
        else:
            return self.exttag
    
    def getParamInfo(self):
        '''
        return IParamInfo instance filled with information from this instance.
        '''
        # for http binding there can only be urlEncoded or urlReplacement and all parts for a
        # message are used.
        porttype = self.operation.binding.wsdl.porttypes[self.operation.binding.porttype]
        porttypeoperation = porttype[self.operation.name]
        message = self.operation.binding.wsdl.messages[porttypeoperation[self.tag]['message']]
        pinfos = []
        for msgpart in message:
            pinfo = ParamInfo()
            # no serializer info needed here.
            pinfo.name = msgpart['name']
            pinfo.type = msgpart['type']
            pinfos.append(pinfo)
        return pinfos

def httpparaminfofactory(operation, inputelem):
    '''
    Factory for HTTPParamInfo instances.
    '''
    paraminfo = HTTPParamInfo(operation)
    paraminfo = paraminfo.frometree(inputelem)
    return paraminfo
directlyProvides(httpparaminfofactory, IWSDLExtensionFactory)
