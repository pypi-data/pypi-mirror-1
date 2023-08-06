'''
RPC Dispatcher Tests
--------------------

'''

import unittest
from rpc4django.rpcdispatcher import *
from rpc4django.jsonrpcdispatcher import *

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

if __name__ == '__main__':
    unittest.main()
