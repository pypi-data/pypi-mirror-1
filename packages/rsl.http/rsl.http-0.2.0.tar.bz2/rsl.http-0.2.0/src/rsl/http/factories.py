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

from rsl.http.schema import createhttpschema
from rsl.http.proxy import HTTPProxy
from rsl.http.serializer import URLEncodeSerializer, URLReplacementSerializer
from rsl.interfaces import IProxyFactory, ISerializer, IDeserializer
from rsl.http.namespace import NS_HTTP
from rsl.interfaces import ISchemaFactory

def register():
    # addons for xsd module
    registerimpl(ISchemaFactory, NS_HTTP, createhttpschema)
    # rsl stuff
    registerimpl(IProxyFactory, NS_HTTP, HTTPProxy)
    # maybe rename urlEncoded to application/x-www-form-urlencoded
    registerimpl(ISerializer, 'application/x-www-form-urlencoded', URLEncodeSerializer)
    registerimpl(IDeserializer, 'application/x-www-form-urlencoded', URLEncodeSerializer)
    registerimpl(ISerializer, 'urlReplacement', URLReplacementSerializer)
