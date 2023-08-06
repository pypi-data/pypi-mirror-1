'''
Tests

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

import unittest
from rpcdispatcher import *
from jsonrpcdispatcher import *

# tests both the class and the decorator
class TestRPCMethod(unittest.TestCase):
    def setUp(self):
        @rpcmethod(name='my.add', signature=['int', 'int', 'int'])
        def add(a,b):
            return a+b
        self.add = RPCMethod(add)
        
        @rpcmethod()
        def test1(arg1):
            return 4
        self.test1 = RPCMethod(test1)
    
    def test_verify_creation(self):
        self.assertEqual(self.add.name, 'my.add')
        self.assertEqual(self.add.signature, ['int', 'int', 'int'])
        self.assertEqual(self.add.args, ['a', 'b'])
        
        self.assertEqual(self.test1.name, 'test1')
        self.assertEqual(self.test1.signature, ['object', 'object'])
        self.assertEqual(self.test1.args, ['arg1'])
    
    def test_get_retrunvalue(self):
        self.assertEqual(self.add.get_returnvalue(), 'int')
        self.assertEqual(self.test1.get_returnvalue(), 'object')
    
    def test_get_params(self):
        self.assertEqual(self.add.get_params(), [{'name': 'a', 'rpctype': 'int'}, {'name': 'b', 'rpctype': 'int'}])
        self.assertEqual(self.test1.get_params(), [{'name': 'arg1', 'rpctype': 'object'}])

class TestRPCDispatcher(unittest.TestCase):
    def setUp(self):
        self.d = RPCDispatcher()
        def add(a,b):
            return a+b
        
        self.add = add
        
    def test_listmethods(self):
        resp = self.d.system_listmethods()
        self.assertEquals(resp, ['system.describe', 'system.listMethods', 'system.methodHelp', 'system.methodSignature'])
        
        self.d.register_method(self.add)
        resp = self.d.system_listmethods()
        self.assertEquals(resp, ['add', 'system.describe', 'system.listMethods', 'system.methodHelp', 'system.methodSignature'])
        
    def test_methodhelp(self):
        resp = self.d.system_methodhelp('system.methodHelp')
        self.assertEquals(resp, 'Returns documentation for a specified method')
        
    def test_methodsignature(self):
        resp = self.d.system_methodsignature('system.listMethods')
        self.assertEquals(resp, ['array'])
        
        resp = self.d.system_methodsignature('system.methodSignature')
        self.assertEquals(resp, ['array', 'string'])
        
    def test_xmlrpc_call(self):
        xml = '<?xml version="1.0"?><methodCall><methodName>system.listMethods</methodName><params></params></methodCall>'
        expresp = "<?xml version='1.0'?><methodResponse><params><param><value><array><data><value><string>system.describe</string></value><value><string>system.listMethods</string></value><value><string>system.methodHelp</string></value><value><string>system.methodSignature</string></value></data></array></value></param></params></methodResponse>"
        resp = self.d.xmldispatch(xml)
        self.assertEqual(resp.replace('\n',''), expresp)
        
    def test_jsonrpc_call(self):
        jsontxt = '{"params":[],"method":"system.listMethods","id":1}'
        expresp = '{"result": ["system.describe", "system.listMethods", "system.methodHelp", "system.methodSignature"], "id": 1, "error": null}'
        resp = self.d.jsondispatch(jsontxt)
        self.assertEqual(resp, expresp)
        
    def test_register_method(self):
        self.d.register_method(self.add)
        
        jsontxt = '{"params":[1,2],"method":"add","id":1}'
        expresp = '{"result": 3, "id": 1, "error": null}'
        resp = self.d.jsondispatch(jsontxt)
        self.assertEqual(resp, expresp)
        
        xml = '<?xml version="1.0"?><methodCall><methodName>add</methodName><params><param><value><int>1</int></value></param><param><value><int>5</int></value></param></params></methodCall>'
        expresp = "<?xml version='1.0'?><methodResponse><params><param><value><int>6</int></value></param></params></methodResponse>"
        resp = self.d.xmldispatch(xml)
        self.assertEqual(resp.replace('\n',''), expresp)

class TestJSONRPCDispatcher(unittest.TestCase):

    def setUp(self):
        def add(a,b):
            return a+b
        def factorial(num):
            if num > 1:
                return num * factorial(num-1)
            else:
                return 1
        self.dispatcher = JSONRPCDispatcher()
        self.dispatcher.register_function(add, 'add')
        self.dispatcher.register_function(factorial, 'fact')

    def test_dispatch_success(self):
        jsontxt = '{"params":[1,2],"method":"add","id":1}'
        resp = self.dispatcher.dispatch(jsontxt)
        self.assertEqual(resp, '{"result": 3, "id": 1, "error": null}')
        
        jsontxt = '{"params":[5],"method":"fact","id":"hello"}'
        resp = self.dispatcher.dispatch(jsontxt)
        self.assertEqual(resp, '{"result": 120, "id": "hello", "error": null}')
        
    def test_method_error(self):
        jsontxt = '{"params":["a"],"method":"fact","id":"hello"}'
        resp = self.dispatcher.dispatch(jsontxt)
        self.assertEqual(resp, '{"result": null, "id": "hello", "error": {"message": "TypeError(\\"unsupported operand type(s) for -: \'unicode\' and \'int\'\\",)", "code": 104, "name": "JSONRPCError"}}')
        
    def test_dispatch_paramserror(self):
        jsontxt = '{"params":[1],"method":"add","id":"4"}'
        resp = self.dispatcher.dispatch(jsontxt)
        self.assertEqual(resp, '{"result": null, "id": "4", "error": {"message": "TypeError(\'add() takes exactly 2 arguments (1 given)\',)", "code": 104, "name": "JSONRPCError"}}')
        
    def test_dispatch_nomethod(self):
        jsontxt = '{"params":[],"method":"add123","id":123}'
        resp = self.dispatcher.dispatch(jsontxt)
        self.assertEqual(resp, '{"result": null, "id": 123, "error": {"message": "method not found", "code": 105, "name": "JSONRPCError"}}')
        
    def test_dispatch_badrequest(self):
        jsontxt = '"params":asdf[14]","method":"add","id":0}'
        resp = self.dispatcher.dispatch(jsontxt)
        self.assertEqual(resp, '{"result": null, "id": "", "error": {"message": "JSON decoding error", "code": 101, "name": "JSONRPCError"}}')
        
        jsontxt = '["should", "be", "a", "Object"]'
        resp = self.dispatcher.dispatch(jsontxt)
        self.assertEqual(resp, '{"result": null, "id": "", "error": {"message": "Cannot decode to a javascript Object", "code": 102, "name": "JSONRPCError"}}')

        jsontxt = '{"params":"shouldbelist","method":"add","id":0}'
        resp = self.dispatcher.dispatch(jsontxt)
        self.assertEqual(resp, '{"result": null, "id": 0, "error": {"message": "params must be a javascript Array", "code": 102, "name": "JSONRPCError"}}')

        jsontxt = '{"params":"[]","method":123,"id":42}'
        resp = self.dispatcher.dispatch(jsontxt)
        self.assertEqual(resp, '{"result": null, "id": 42, "error": {"message": "method must be a javascript String", "code": 102, "name": "JSONRPCError"}}')

if __name__ == '__main__':
    unittest.main()
