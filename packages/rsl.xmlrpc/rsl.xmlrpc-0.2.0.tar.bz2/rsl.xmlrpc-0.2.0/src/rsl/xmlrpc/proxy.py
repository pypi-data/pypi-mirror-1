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
this module provides an IProxy and IProxyFactory implementation to support
xmlrpc in rsl.
'''
from urlparse import urlparse
from zope.interface import implements, classProvides

from rsl.interfaces import ISerializer, IDeserializer, ITransport
from rsl.interfaces import IProxyFactory, IProxy
from rsl.globalregistry import lookupimpl
from rsl.implementations import OperationInfo

class XMLRPCProxy(object):
    '''
    An implementation of IProxy and IProxyFactory for the XMLRPC-protocol.
    '''
    
    implements(IProxy)
    classProvides(IProxyFactory)
    
    ptype = 'xmlrpc'
    
    def __init__(self, location=None):
        super(XMLRPCProxy, self).__init__()
        self.callables = {}
        self.namegroup = {}
        self.location = location
        
    def addOperation(self, name, operationinfo):
        '''
        name ... name of operation should be a legal python identifier.
        
        operationinfo ... an IOperationInfo instance
        
        TODO: make this more like jsonrpc proxy. 
        '''
        func = Callable(self.location, name, operationinfo)
        if '.' in name:
            # allow direct access with callables array for dotted names
            self.callables[name] = func
        self.addfunction(name, func)
        
    def callRemote(self, name, *args, **kws):
        '''
        Invoke a remote method.
        
        name ... the name of the operation
        *args, **kws ... parameters to pass
        '''
        return self.__getattr__(name)(*args, **kws)
        
    def addfunction(self, name, func):
        '''
        Helper function to support method names with a '.' inside.
        '''
        if '.' in name:
            self.addgroupedoperation(name, func)
        else:
            self.callables[name] = func

    def addgroupedoperation(self, name, func):
        '''
        Help function which manages method names with a '.' inside.
        '''
        if '.' in name:
            namegroup, methodname = name.split('.', 1)
            if namegroup not in self.namegroup:
                self.namegroup[namegroup] = XMLRPCProxy(self.location)
            self.namegroup[namegroup].addfunction(methodname, func)
        
        
    def __getattr__(self, name):
        '''
        return callable for name. 
        
        In XMLRPC a server does not need to be introspectable, so any method 
        name can be an offered method by the service, so just return a 
        callable for it. One special thing about XMLRPC is, that methods can 
        contain '.' in the name. This is also supported by this proxy.
        '''
        if name in self.callables:
            return self.callables[name]
        if name in self.namegroup:
            return self.namegroup[name]
        return Callable(self.location, name)
        
class Callable(object):
    '''
    A callable class which actually executes the xmlrpc remote call.
    '''
    
    serializer = 'XMLRPCSerializer'
    
    paramnames = None
    
    def __init__(self, target, name, operationinfo=None):
        '''
        initialises this callable instance with a remote url (target), a 
        method name (name) and additional information in operationinfo 
        (if available).
        '''
        if operationinfo is None:
            self.operationinfo = OperationInfo()
        else:
            self.operationinfo = operationinfo
        self.operationinfo.name = self.name = name
        self.operationinfo.location = self.location = target
        if self.operationinfo.input is not None:
            # TODO: paramnames is not true... normally there are only type 
            #       infos available
            self.paramnames = [p.name for p in self.operationinfo.input]
        if self.operationinfo.serializer is not None:
            self.serializer = self.operationinfo.serializer
        else:
            self.operationinfo.serializer = self.serializer
        self.__doc__ = getattr(self.operationinfo, 'doc', None)
        # TODO: not really used anywhere or defined
        #self.returntype = operationinfo.output[0].type
        
    def __getattr__(self, name):
        '''
        If this callable has methods under it (separated with '.') then 
        return a new callable.
        '''
        return Callable(self.location, '.'.join((self.name, name)), 
                        self.operationinfo)
    
    def __call__(self, *args):
        '''
        Extend xmlrpc interface with named parameters. The parameter names 
        should be of the form parXX .. where XX is an integer position to 
        place the parameter name int the args array.
        '''
        serializer = lookupimpl(ISerializer, self.serializer)
        headers, reqdata = serializer.serialize(args, self.operationinfo)
        _, data = self.send(reqdata, headers)
        deserializer = lookupimpl(IDeserializer, self.serializer)
        _, result = deserializer.deserialize(data, self.operationinfo) 
        return result
        
    def send(self, data, headers):
        '''
        do the actual wire transfer here and return the response object from 
        an ITransport.
        '''
        pdu = urlparse(self.location)
        transport = lookupimpl(ITransport, pdu.scheme)
        return transport.send(self.location, data, headers=headers)
