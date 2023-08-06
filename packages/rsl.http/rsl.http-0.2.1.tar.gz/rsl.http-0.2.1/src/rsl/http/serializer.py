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
this module implements all de/serialisers defied in WSDL 1 for http encoding.
'''
from urllib import urlencode
from cgi import parse_qs

from zope.interface import classProvides

from rsl.interfaces import ISerializer, IDeserializer

class URLEncodeSerializer(object):
    '''
    The urlencoded serialiser.
    '''
    
    classProvides(ISerializer, IDeserializer)
    
    @classmethod
    def serialize(cls, params, operationinfo, **_):
        '''
        params    ... dict of values to serialise
        operationinfo ... an IOperationinfo
        '''
        encodedparams = {}
        for pinfo in operationinfo.input:
            ptype = operationinfo.typesystem.getType(pinfo.type)
            encodedparams[pinfo.name] = ptype.encode(params[pinfo.name])
        return ({'Content-Type': 'application/x-www-form-urlencoded'},
                urlencode(encodedparams, True))
        
    @classmethod
    def deserialize(cls, data, operationinfo, **_):
        '''
        extracts parameter names and values from urlencoded data.
        '''
        return None, parse_qs(data, True)

class URLReplacementSerializer(object):
    '''
    the WSDL 1 URL-replacement serialiser.
    '''
    
    classProvides(ISerializer)
    
    @classmethod
    def serialize(cls, params, operationinfo, **_):
        '''
        params    ... dict of values to serialise
        operationinfo ... an IOperationinfo
        '''
        encodedparams = {}
        for pinfo in operationinfo.input:
            ptype = operationinfo.typesystem.getType(pinfo.type)
            encodedparams[pinfo.name] = ptype.encode(params[pinfo.name])
        template = operationinfo.location
        for key, value in encodedparams.items():
            template.replace('(%s)' % key, value)
            # TODO: possibly dangerous, if replacement matches pattern for another
            #       replacement
            #       should the values be url encoded?
        return (None, template)
            