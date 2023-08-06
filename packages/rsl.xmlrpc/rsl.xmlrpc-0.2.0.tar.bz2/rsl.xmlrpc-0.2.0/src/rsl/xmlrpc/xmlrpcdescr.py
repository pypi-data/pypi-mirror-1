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
provides IServiceDescription module for rsl, which handles XMLRPC descriptions.
'''
from itertools import izip, islice
from xmlrpclib import MultiCall

from zope.interface import implements

from rsl.globalregistry import lookupimpl
from rsl.implementations import OperationInfo, ParamInfo
from rsl.interfaces import IServiceDescription, IProxyFactory

def loadXMLRPC(url):
    '''
    returns an IServiceDescription object given a xmlrpc-url.
    '''
    desc = XMLRPCDescr()
    desc.fromURL(url)
    return desc

class XMLRPCDescr(object):
    '''
    The actual XMLRPC IServiceDescription implementation
    '''
    
    implements(IServiceDescription)
    
    descname = 'xmlrpc'
    
    def __init__(self):
        '''
        create the XMLRPCDescr instance and reset all values.
        '''
        super(XMLRPCDescr, self).__init__()
        self.url = None
        self.methods = None
        
    def fromURL(self, url, **kws):
        '''
        accepts inspect as additional parameter.
        if inspect is False then automatic introspection is not executed.
        '''
        self.url = url
        if 'inspect' in kws and not kws['inspect']:
            return 
        self.inspect()
        
    def getProxy(self, **_):
        '''
        return an IProxy instance for XMLRPC.
        '''
        proxyfac = lookupimpl(IProxyFactory, 'XMLRPCProxy')
        proxy = proxyfac(self.url)
        if self.methods:
            for methodname, methodinfo in self.methods.items():
                proxy.addOperation(methodname, methodinfo)
        return proxy
        
    def inspect(self):
        '''
        tries to inspect the remote endpoint to pre initialise all
        offered methods at this proxy.
        '''
        # TODO: use standard xmlrpclib Multicall objects.
        proxy = self.getProxy()
        #1. get list of methods.
        methodlist = proxy.system.listMethods()
        mcall = MultiCall(proxy)
        for method in methodlist:
            mcall.system.methodSignature(method)
            mcall.system.methodHelp(method)
        result = mcall()
        rzi = izip(methodlist, izip(islice(result, 0, None, 2), 
                                    islice(result, 1, None, 2)))
        self.methods = {}
        for methodname, (signature, doc) in rzi:
            opinfo = OperationInfo()
            opinfo.name = methodname
            opinfo.serializer = 'XMLRPCSerializer'
            opinfo.location = self.url
            # TODO: signature is a list of signatures.... I would say just 
            #       take the longest.
            #       I assume, that overloaded signatures, just add something 
            #       to the end, so string len comparison is enough
            #       If types ate the start change, then this filter does not 
            #       work correctly.
            longestsig = ''
            for sig in signature:
                if len(sig) > len(longestsig):
                    longestsig = sig
            sig = longestsig.split(',')
            opinfo.doc = doc
            pinfo = ParamInfo()
            pinfo.type = sig[0]
            opinfo.output = [pinfo]
            opinfo.input = []
            for sigitem in sig[1:]:
                pinfo = ParamInfo()
                pinfo.type = sigitem
                opinfo.input.append(pinfo)
            self.methods[methodname] = opinfo
            
    def getServices(self):
        '''
        return all service names offered by this proxy.
        '''
        return [{'name': self.url}] 
