'''
JSON RPC Dispatcher Tests
-------------------------

'''

import unittest
from rpc4django.jsonrpcdispatcher import *

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
        jsondict = json.loads(resp)
        self.assertTrue(jsondict['result'] is None)
        self.assertTrue(jsondict['error'] is not None)

    def test_dispatch_paramserror(self):
        jsontxt = '{"params":[1],"method":"add","id":"4"}'
        resp = self.dispatcher.dispatch(jsontxt)
        jsondict = json.loads(resp)
        self.assertTrue(jsondict['result'] is None)
        self.assertTrue(jsondict['error'] is not None)

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
