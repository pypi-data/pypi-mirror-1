##############################################################################
# Copyright 2008-2009, Gerhard Weis
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
this module provides JSON-RPC 1.0 proxy implementations for rls.
'''
from urlparse import urljoin, urlparse

from zope.interface import implements, classProvides

from rsl.interfaces import IProxy, IProxyFactory, ISerializer 
from rsl.interfaces import IDeserializer, ITransport
from rsl.globalregistry import lookupimpl
from rsl.implementations import OperationInfo

class JSONRPCProxy(object):
    '''
    The JSON-RPC 1.0 proxy implementation.
    '''
    
    implements(IProxy)
    classProvides(IProxyFactory)
    
    ptype = 'JSON-RPC-1.0'
    
    def __init__(self, location):
        '''
        create proxy instance.
        '''
        super(JSONRPCProxy, self).__init__()
        self.callables = {}
        self.namegroup = {}
        self.location = location
        
    def addOperation(self, name, operationinfo):
        '''
        name ... name of operation should be a legal python identifier.
        
        operationfo ... an IOperationInfo instance which holds detailled
                        information about operation. 
        '''
        target = self.location
        target = urljoin(target, operationinfo.location)
        func = Callable(target, name, operationinfo)
        if '.' in name:
            # allow direct access with callables array for dotted names
            self.callables[name] = func
        self.addFunction(name, func)
        
    def callRemote(self, name, *args, **kws):
        '''
        JSON-RPC 1.0 only supports positional arguments.
        '''
        return getattr(self, name)(*args, **kws)
        
    def addFunction(self, name, func):
        '''
        helper function to handle dotted method names. 
        '''
        if '.' in name:
            self.addGroupedOperation(name, func)
        else:
            self.callables[name] = func

    def addGroupedOperation(self, name, func):
        '''
        helper function to handle dotted method names.
        '''
        if '.' in name:
            namegroup, methodname = name.split('.', 1)
            if namegroup not in self.namegroup:
                self.namegroup[namegroup] = JSONRPCProxy(self.location)
            self.namegroup[namegroup].addFunction(methodname, func)
        
        
    def __getattr__(self, name):
        '''
        return callable for name. 
        
        In JSONRPC a server does not need to be introspectable, so any method 
        name can be an offered method by the service, so just return a 
        callable for it. One special thing about JSONRPC is, that methods can 
        contain '.' in the name. This is also supported by this proxy.
        '''
        if name in self.callables:
            return self.callables[name]
        if name in self.namegroup:
            return self.namegroup[name]
        return Callable(self.location, name)

class Callable(object):
    '''
    a python callable which actually calls the remote service.
    '''
    
    serializer = 'JSON-RPC-1.0'
    
    paramnames = None
    
    def __init__(self, target, name, operationinfo=None):
        '''
        initialise this callable with as much information as available.
        '''
        if operationinfo is None:
            self.operationinfo = OperationInfo()
        else:
            self.operationinfo = operationinfo
        self.operationinfo.name = self.name = name
        self.operationinfo.location = self.location = target
        if self.operationinfo.input is not None:
            self.paramnames = [p.name for p in self.operationinfo.input]
        if self.operationinfo.serializer is not None:
            self.serializer = self.operationinfo.serializer
        else:
            self.operationinfo.serializer = self.serializer
            
        
    def __getattr__(self, name):
        '''
        for dotted method names return the sub callable.
        '''
        return Callable(self.location, '.'.join((self.name, name)), 
                        self.operationinfo)
    
    def __call__(self, *args):
        '''
        do the actual remote invocation.
        
        TODO: how about named parameters?
              it is only possible to use one variant.. named or positional 
              params. JSON-RPC 1.0 only supports positional params on the wire
        '''
        serializer = lookupimpl(ISerializer, self.serializer)
        reqheaders, reqdata = serializer.serialize(args, self.operationinfo)
        _, data = self.send(reqdata, reqheaders)
        deserializer = lookupimpl(IDeserializer, self.serializer)
        _, result = deserializer.deserialize(data, self.operationinfo) 
        return result
        
        
    def send(self, data, headers):
        '''
        send and receive payload.
        '''
        pdu = urlparse(self.location)
        transport = lookupimpl(ITransport, pdu.scheme)
        return transport.send(self.location, data, headers=headers)
