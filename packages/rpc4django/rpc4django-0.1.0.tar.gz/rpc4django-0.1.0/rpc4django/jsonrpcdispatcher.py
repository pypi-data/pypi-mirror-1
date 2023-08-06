'''
JSONRPC Dispatcher

This module contains the jsonrpc dispatcher class.

see http://json-rpc.org/wiki/specification

Copyright (c) 2009, David Fischer
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    * Neither the name of rpc4django nor the
      names of its contributors may be used to endorse or promote products
      derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY David Fischer ''AS IS'' AND ANY
EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL David Fischer BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''

from types import StringTypes

# attempt to import json from 3 sources:
# 1. try to import it from django
# 2. if this is not run through django, try to import the simplejson module
# 3. import the json module that is only present in python >= 2.6
try:
    from django.utils import simplejson as json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        import json

# These error codes may be defined by the json-rpc spec at a later date
# see http://json-rpc.org/wd/JSON-RPC-1-1-WD-20060807.html#ErrorObject
JSONRPC_SERVER_ERROR = 100
JSONRPC_PARSE_ERROR = 101
JSONRPC_BAD_CALL_ERROR = 102
JSONRPC_SEQUENCE_ERROR = 103
JSONRPC_SERVICE_ERROR = 104
JSONRPC_PROCEDURE_NOT_FOUND_ERROR = 105
    
    
class JSONRPCDispatcher:
    '''
    JSONRPC Dispatcher
    
    This class can be used encode and decode jsonrpc messages, dispatch
    the requested method with the passed parameters, and return any response
    or error.
    '''
    
    def __init__(self):
        self.methods = {}
    
    def register_function(self, method, external_name):
        '''
        Registers a method with the jsonrpc dispatcher.
        
        This method can be called later via the dispatch method.
        '''
        self.methods[external_name] = method
    
    def _encode_result(self, jsonid, result, error):
        res = {'id': jsonid}
        
        if error is None:
            res['error'] = None
            res['result'] = result
        else:
            res['error'] = error
            res['error']['name'] = 'JSONRPCError'
            res['result'] = None
            
        try:
            return json.dumps(res)
        except:
            err = {'message': 'failed to encode return value',
                   'code': JSONRPC_SERVICE_ERROR,
                   'name': 'JSONRPCError'}
                
            res['result'] = None
            res['error'] = err
            return json.dumps(res)
    
    def dispatch(self, json_data):
        '''
        Verifies that the passed json encoded string 
        is in the correct form according to the json-rpc spec
        and calls the appropriate method
        
        Checks:
         1. that the string encodes into a javascript Object (dictionary)
         2. that 'method' and 'params' are present
         3. 'method' must be a javascript String type
         4. 'params' must be a javascript Array type
         
        Returns:
         the JSON encoded response
        '''
        
        try:
            # attempt to do a json decode on the data
            jsondict = json.loads(json_data)
        except ValueError:
            return self._encode_result('', None, 
                    {'message': 'JSON decoding error', 
                     'code': JSONRPC_PARSE_ERROR})
        
        if not isinstance(jsondict, dict):
            # verify the json data was a javascript Object which gets decoded
            # into a python dictionary
            return self._encode_result('', None, 
                    {'message': 'Cannot decode to a javascript Object', 
                     'code': JSONRPC_BAD_CALL_ERROR})
        
        if not 'method' in jsondict or not 'params' in jsondict:
            # verify the dictionary contains the correct keys
            # for a proper jsonrpc call
            return self._encode_result(jsondict.get('id', ''), None, 
                    {'message': "JSONRPC requests must have the "+ \
                     "attributes 'method' and 'params'", 
                     'code': JSONRPC_BAD_CALL_ERROR})
        
        if not isinstance(jsondict['method'], StringTypes):
            return self._encode_result(jsondict.get('id', ''), None, 
                    {'message': 'method must be a javascript String', 
                     'code': JSONRPC_BAD_CALL_ERROR})
        
        if not isinstance(jsondict['params'], list):
            return self._encode_result(jsondict.get('id', ''), None, 
                    {'message': 'params must be a javascript Array', 
                     'code': JSONRPC_BAD_CALL_ERROR})
        
        
        if jsondict['method'] in self.methods:
            try:
                result = self.methods[jsondict.get('method')] \
                                    (*jsondict.get('params')) 
            except Exception, e:
                # this catches any error from the called method raising
                # an exception to the wrong number of params being sent
                # to the method.
                return self._encode_result(jsondict.get('id', ''), None, 
                            {'message': repr(e), 
                             'code': JSONRPC_SERVICE_ERROR})
            return self._encode_result(jsondict.get('id', ''), result, None)
        else:
            return self._encode_result(jsondict.get('id', ''), None, 
                    {'message': 'method not found',  
                     'code': JSONRPC_PROCEDURE_NOT_FOUND_ERROR})

    