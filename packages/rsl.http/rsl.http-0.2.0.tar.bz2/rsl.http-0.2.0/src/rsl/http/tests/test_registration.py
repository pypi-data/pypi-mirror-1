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
import unittest

from zope.interface.verify import verifyClass, verifyObject

from rsl.globalregistry import lookupimpl
from rsl.interfaces import ISchemaFactory, ISchema, IServiceDescription
from rsl.interfaces import IProxyFactory, IProxy, ISerializer, IDeserializer
from rsl.wsdl1.interfaces import IBinding, IOperation, IParamInfo, IFault
from rsl.wsdl1.interfaces import IPort, IWSDLExtensionFactory
from rsl.wsdl1.wsdl import findextensionfactory
from rsl.http.namespace import NS_HTTP
from rsl.http.wsdl1 import HTTPPort, HTTPBinding, HTTPOperation, HTTPParamInfo

class TestRegistration(unittest.TestCase):
    
    def test_interfaces(self):
        obj = lookupimpl(ISchemaFactory, NS_HTTP)
        verifyObject(ISchemaFactory, obj)
        verifyObject(ISchema, obj(None))
        obj = lookupimpl(IProxyFactory, NS_HTTP)
        verifyObject(IProxyFactory, obj)
        verifyClass(IProxy, obj)
        obj = lookupimpl(ISerializer, 'application/x-www-form-urlencoded')
        verifyObject(ISerializer, obj)
        obj = lookupimpl(ISerializer, 'urlReplacement')
        verifyObject(ISerializer, obj)
        obj = lookupimpl(IDeserializer, 'application/x-www-form-urlencoded')
        verifyObject(IDeserializer, obj)
        
    def test_wsdlextensions(self):
        obj = findextensionfactory('rsl.wsdl1.service.port', NS_HTTP)
        verifyObject(IWSDLExtensionFactory, obj)
        verifyClass(IPort, HTTPPort)
        obj = findextensionfactory('rsl.wsdl1.binding', NS_HTTP)
        verifyObject(IWSDLExtensionFactory, obj)
        verifyClass(IBinding, HTTPBinding)
        obj = findextensionfactory('rsl.wsdl1.binding.operation', NS_HTTP)
        verifyObject(IWSDLExtensionFactory, obj)
        verifyClass(IOperation, HTTPOperation)
        obj = findextensionfactory('rsl.wsdl1.binding.operation.input', NS_HTTP)
        verifyObject(IWSDLExtensionFactory, obj)
        obj = findextensionfactory('rsl.wsdl1.binding.operation.output', NS_HTTP)
        verifyObject(IWSDLExtensionFactory, obj)
        verifyClass(IParamInfo, HTTPParamInfo)

def test_suite():
    loader = unittest.TestLoader()
    return unittest.TestSuite([loader.loadTestsFromTestCase(TestRegistration),
                               ])
