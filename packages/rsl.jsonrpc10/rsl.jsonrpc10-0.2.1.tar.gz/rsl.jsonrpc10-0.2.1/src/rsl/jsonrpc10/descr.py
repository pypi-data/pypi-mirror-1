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
JSON-RPC can also be used just with a url.
see xml-rpc description for this method.

TODO: currently this is just a factory for unspecified JSON-RPC proxies.
      add support for at least xml-rpc introspection methods. but this may be 
      more legal for an 1.1 implementation.
'''
from zope.interface import implements

from rsl.interfaces import IServiceDescription, IProxyFactory
from rsl.globalregistry import lookupimpl

#in theory json-rpc may support xmlrpc-multicall style... 
#should be noproblem to use xmlrpclib.Multicall class for this
#from xmlrpclib import MultiCall

class JSONRPCDescr(object):
    '''
    A IServiceDescription for JSON-RPC 1.0
    '''
    
    implements(IServiceDescription)
    
    descname = 'JSON-RPC-1.0'
    
    def __init__(self):
        '''
        create an empty object.
        '''
        super(JSONRPCDescr, self).__init__()
        self.url = None
        
    def fromURL(self, url, **kws):
        '''
        initialise this description from url.
        '''
        self.url = url
        
    def getProxy(self, **kws):
        '''
        return an IProxy according to this service description.
        '''
        proxyfac = lookupimpl(IProxyFactory, 'JSON-RPC-1.0')
        proxy = proxyfac(self.url)
        return proxy
    
    def getServices(self):
        '''
        return all service names described by this description.
        '''
        return [{'name': self.url}]
