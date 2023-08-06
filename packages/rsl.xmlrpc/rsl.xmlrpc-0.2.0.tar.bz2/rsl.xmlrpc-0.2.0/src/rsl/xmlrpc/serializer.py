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
this module provides an ISerialiser and IDeserialiser implementation
for XMLRPC which plugs into rsl.
'''
from string import Template
from xmlrpclib import loads, dumps

from zope.interface import classProvides

from rsl.interfaces import ISerializer, IDeserializer

class XMLRPCSerializer(object):
    '''
    ISerialiser and IDeserialiser implementation for XMLRPC.
    '''
    
    classProvides(ISerializer, IDeserializer)
    
    #XMLRPC_TEMPLATE = Template("<?xml version='1.0' encoding='utf-8'?>\n
    #                             <methodCall>
    #                                 <methodName>${method}</methodName>
    #                                 ${params}
    #                             </methodCall>")
    XMLRPC_TEMPLATE = Template("<methodCall><methodName>${method}</methodName>${params}</methodCall>")
    
    @classmethod
    def serialize(cls, data, operationinfo, **_):
        '''
        serialise data in data-dictionary according to information in 
        operationinfo.
        '''
        reqdata = cls.XMLRPC_TEMPLATE.substitute(method=operationinfo.name,
                                            params=dumps(data, allow_none=True))
        return {'Content-type': 'text/xml'}, reqdata
    
    @classmethod
    def deserialize(cls, data, operationinfo, **_):
        '''
        Parse an xmlrpc response.
        
        Return only first param, if there is one, because xmlrpc allows only
        one param in a response message. 
        '''
        params, _ = loads(data, use_datetime=True)
        if len(params) > 0:
            return None, params[0]
        return None, None
