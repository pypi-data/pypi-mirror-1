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
this module provides json-rpc de/serialisers for rsl.
'''
from zope.interface import classProvides
from simplejson import loads, dumps

from rsl.interfaces import ISerializer, IDeserializer

class JSONRPCException(Exception):
    '''
    An exception class, to signal a returned fault.
    '''
    
    def __init__(self, rpcerror):
        Exception.__init__(self)
        self.error = rpcerror

class JSONRPCSerializer(object):
    '''
    This serializer creates the JSON RPC 1.0 envelope....
    and can also decode a JSON RPC 1.0 envelope.
    '''
    
    classProvides(ISerializer, IDeserializer)
    
    @classmethod
    def serialize(cls, data, operationinfo, **kws):
        '''
        Create envelope and serialize all given data with JSON.
        
        TODO: try to create some sort of unique id here
        TODO: maybe make JSON serializer also available over registry. so JSON impl is configurable.
              this serialiser only adds the json-rpc 1.0 specific envelope data.
        '''
        wrappeddata = {'method': operationinfo.name,
                       'params': data,
                       'id': 'json-rpc'}
        return ({'Content-type': 'application/json'}, dumps(wrappeddata))
    
    @classmethod
    def deserialize(cls, data, operationinfo, **kws):
        '''
        Parse an jsonrpc response. Remove envelope, check for errors and return result.
        '''
        response = loads(data)
        error = response.get('error', None) 
        if  error is not None:
            raise JSONRPCException(error)
        return (None, response['result'])
    