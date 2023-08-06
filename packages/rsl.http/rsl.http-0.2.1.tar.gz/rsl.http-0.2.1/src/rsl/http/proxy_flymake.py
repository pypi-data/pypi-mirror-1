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
this module implements a proxy for http-protocol defined in WSDL 1.
it's usage is probably not restricted to WSDL 1 defined web-services.
'''
from urlparse import urljoin, urlsplit

from zope.interface import implements, classProvides

from rsl.globalregistry import lookupimpl
from rsl.interfaces import ITransport, ISerializer, IDeserializer
from rsl.interfaces import IProxy, IProxyFactory
from rsl.http.namespace import NS_HTTP 

class HTTPProxy(object):
    '''
    This class provides the IProxyFactory interface and instances of it
    provide the IProxy interface.
    '''
    
    implements(IProxy)
    classProvides(IProxyFactory)
    
    ptype = NS_HTTP
    
    def __init__(self, url, name=None):
        '''
        create empty HTTPProxy instance.
        '''
        super(HTTPProxy, self).__init__()
        self.callables = {}
        self.location = url
        self.name = name
        
    def __getattr__(self, name):
        '''
        map available method names to python methods.
        '''
        if name in self.callables:
            return self.callables[name]
        raise AttributeError
    
    def callRemote(self, name, *args, **kws):
        '''
        call named remote method.
        '''
        self.__getattr__(name)(*args, **kws)
        
    def addOperation(self, name, operationinfo):
        '''
        Tells this proxy, that an operation named 'name' exists, and
        all necessary information about this operation are in operationinfo
        which is an IOperationInfo instace.
        '''
        #operation: name, soapAction, style,
        #           input, output, faults
        func = Callable(self.location, name, operationinfo)
        self.callables[name] = func

class Callable(object):
    ''' 
    a callable needs to know the endpoint (port)
    the transport (binding)
    and the encoding (operation)
    
    To modify the transport, just extend the transportfactory
    or set a specific transport directly on the binding
    '''
    
    def __init__(self, target, name, operationinfo):
        '''
        initialise this callable.
        '''
        self.target = target
        self.name = name
        self.operationinfo = operationinfo
        self.paramnames = [par.name for par in operationinfo.input]
        self.method = getattr(operationinfo, 'method', None)
        
    def __call__(self, *args, **kws):
        ''' 
        execute the actual remote call.
        possible kws: _headers, _attrs 
        '''
        headers, payload = self.serialize(*args, **kws)
        
        base = self.target
        url = self.operationinfo.location

        if self.operationinfo.serializer == 'urlReplacement':
            url = payload
            payload = None
        # ok merge base with relative url
        if url.startswith('/'): 
            # hack for wrong relative urls in asmx files.May introduce 
            # problems with other resources but for now it is here.
            # quite normal for MS to interpret base and relative uri's
            # different than all others
            if not base.endswith('/'):
                base = base + '/'
            url = url[1:]
        url = urljoin(base, url)
        if self.method in ('GET', 'DELETE', 'HEAD'):
            if payload is not None:
                url = url + '?' + payload
                payload = None
        # send data
        headers, response = self.send(url, payload, headers)    
        # TODO: various unpack options
        return self.deserialize(headers, response)
    
    def serialize(self, *args, **kws):
        '''
        serialises the given args according with the help of the required
        serialiser.
        '''
        # prepare params
        params = {} 
        print "Paramnames:", self.paramnames
        if self.paramnames:
            pnames = self.paramnames[:]
            for arg in args:
                if pnames:
                    params[pnames.pop(0)] = arg
        # TODO: kw-param could overwrite non-kw param...
        params.update(kws)
        print "Params:", params
        
        # get xml schema serialiser and encode all params into map
        serialiser = lookupimpl(ISerializer, self.operationinfo.serializer)
        return serialiser.serialize(params, self.operationinfo)

    def deserialize(self, headers, response):
        '''
        deserialises the given args according with the help of the required
        deserialiser.
        '''
        serialiser = lookupimpl(IDeserializer, self.operationinfo.deserializer)
        headers, payload = serialiser.deserialize(response, self.operationinfo,
                                                  headers=headers)
        return headers, payload

    def send(self, addr, payload, headers):
        '''
        Sends the serialised request with the help of an ITransport instance for
        the required protocol.
        '''
        usp = urlsplit(addr)
        transport = lookupimpl(ITransport,  usp.scheme)        
        return transport.send(addr, payload, method=self.method,
                              headers=headers)    
