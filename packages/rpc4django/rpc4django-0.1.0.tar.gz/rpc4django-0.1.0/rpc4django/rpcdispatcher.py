'''
RPC Dispatcher

This module contains the classes necessary to handle both
jsonrpc and xmlrpc requests. It also contains a decorator to
mark methods as rpc methods.

see http://www.xmlrpc.com/
see http://json-rpc.org/

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

import platform
import inspect
import pydoc
from SimpleXMLRPCServer import SimpleXMLRPCDispatcher
from jsonrpcdispatcher import JSONRPCDispatcher


def rpcmethod(**kwargs):
    '''
    Accepts keyword based arguments that describe the method's rpc aspects

    EXAMPLES:
    @rpcmethod()
    @rpcmethod(name='myns.myFuncName', signature=['int','int'])
    '''
    
    def set_rpcmethod_info(method):
        method.is_rpcmethod = True
        method.signature = []
        method.external_name = getattr(method, '__name__')

        if 'name' in kwargs:
            method.external_name = kwargs['name']

        if 'signature' in kwargs:
            method.signature = kwargs['signature']

        return method
    return set_rpcmethod_info


class RPCException(Exception):
    '''
    An exception (which translates to an xmlrpc fault or jsonrpc error)
    for the system or user methods to throw.
    '''
    
    pass


class RPCMethod:
    '''
    A method available via the rpc dispatcher
    '''
    
    def __init__(self, method, name=None, signature=None, docstring=None):
        self.method = method
        self.help = ''
        self.signature = []
        self.name = ''
        self.args = []
        
        # set the method name based on @rpcmethod or the passed value
        # default to the actual method name
        if hasattr(method, 'external_name'):
            self.name = method.external_name
        elif name is not None:
            self.name = name
        else:
            self.name = method.func_name
            
        # get the help string for each method
        if docstring is not None:
            self.help = docstring
        else:
            self.help = pydoc.getdoc(method)
            
        # use inspection (reflection) to get the arguments
        args, varargs, keywords, defaults = inspect.getargspec(method)
        self.args = [arg for arg in args if arg != 'self']
        self.signature = ['object' for arg in self.args]
        self.signature.insert(0, 'object')
        
        if hasattr(method, 'signature') and \
             len(method.signature) == len(self.args) + 1:
            # use the @rpcmethod signature if it has the correct
            # number of args
            self.signature = method.signature
        elif signature is not None and len(self.args) + 1 == len(signature):
            # use the passed signature if it has the correct number
            # of arguments
            self.signature = signature
            
    def get_returnvalue(self):
        '''
        Returns the return value which is the first element of the signature
        '''
        if len(self.signature) > 0:
            return self.signature[0]
        return None
        
    def get_params(self):
        '''
        Returns a list of dictionaries containing name and type of the params
        
        eg. [{'name': 'arg1', 'type': 'int'}, {'name': 'arg2', 'type': 'int'}]
        '''
        if len(self.signature) > 0:
            arglist = []
            if len(self.signature) == len(self.args) + 1:
                for argnum in range(len(self.args)):
                    arglist.append({'name': self.args[argnum], \
                                    'rpctype': self.signature[argnum+1]})
                return arglist
            else:
                # this should not happen under normal usage
                for argnum in range(len(self.args)):
                    arglist.append({'name': self.args[argnum], \
                                    'rpctype': 'object'})
                return arglist
        return []


class RPCDispatcher:
    '''
    Dispatches method calls to either the xmlrpc or jsonrpc dispatcher
    '''
    
    def __init__(self, apps=[], restrict_introspection=False):
        version = platform.python_version_tuple()
        self.rpcmethods = []
        self.jsonrpcdispatcher = JSONRPCDispatcher()
        
        if int(version[0]) < 3 and int(version[1]) < 5:
            # this is for python 2.4 and below
            self.xmlrpcdispatcher = SimpleXMLRPCDispatcher()
        else:
            # python 2.5+ requires different parameters
            self.xmlrpcdispatcher = SimpleXMLRPCDispatcher(allow_none=False, 
                                                           encoding=None)
            
        if not restrict_introspection:
            self.register_method(self.system_listmethods)
            self.register_method(self.system_methodhelp)
            self.register_method(self.system_methodsignature)
            self.register_method(self.system_describe)
            
        self.register_rpcmethods(apps)
        
    @rpcmethod(name='system.describe', signature=['struct'])
    def system_describe(self):
        '''
        Returns a simple method description of the methods supported
        '''
        
        description = {}
        description['serviceType'] = 'RPC4Django'
        description['serviceURL'] = '/RPC2'         # TODO: Change this!
        description['methods'] = [{'name': method.name, 
                                   'summary': method.help, 
                                   'params': method.get_params(),
                                   'return': method.get_returnvalue()} \
                                  for method in self.rpcmethods]
        
        return description
    
    @rpcmethod(name='system.listMethods', signature=['array'])
    def system_listmethods(self):
        '''
        Returns a list of supported methods
        '''
        
        methods = [method.name for method in self.rpcmethods]
        methods.sort()
        return methods
    
    @rpcmethod(name='system.methodHelp', signature=['string', 'string'])
    def system_methodhelp(self, method_name):
        '''
        Returns documentation for a specified method
        '''
        
        for method in self.rpcmethods:
            if method.name == method_name:
                return method.help
            
        # this differs from what implementation in SimpleXMLRPCServer does
        # this will report via a fault or error while SimpleXMLRPCServer
        # just returns an empty string
        raise RPCException('No method found with name: '+str(method_name))
          
    @rpcmethod(name='system.methodSignature', signature=['array', 'string'])
    def system_methodsignature(self, method_name):
        '''
        Returns the signature for a specified method 
        
        eg. [retval, arg1, arg2,...]
        '''
        
        for method in self.rpcmethods:
            if method.name == method_name:
                return method.signature
        raise RPCException('No method found with name: '+str(method_name))
               
    def register_rpcmethods(self, apps):
        '''
        Scans the installed apps for methods with the rpcmethod decorator
        Adds these methods to the list of methods callable via RPC
        '''    
        
        for appname in apps:
            # check each app for any rpcmethods
            app = __import__(appname, globals(), locals(), ['*'])
            for obj in dir(app):
                method = getattr(app, obj)
                if callable(method) and \
                   getattr(method, 'is_rpcmethod', False):
                    # if this method is callable and it has the rpcmethod
                    # decorator, add it to the dispatcher
                    self.register_method(method, method.external_name)     
    
    def jsondispatch(self, raw_post_data):
        '''
        Sends the post data to a jsonrpc processor
        '''
        
        return self.jsonrpcdispatcher.dispatch(raw_post_data)
    
    def xmldispatch(self, raw_post_data):
        '''
        Sends the post data to an xmlrpc processor
        '''
        
        return self.xmlrpcdispatcher._marshaled_dispatch(raw_post_data)
        
    def list_methods(self):
        '''
        Returns a list of RPCMethod objects supported by the server
        '''
        
        return self.rpcmethods
    
    def register_method(self, method, name=None, signature=None, helpmsg=None):
        '''
        Registers a method with the rpc server
        '''
        
        meth = RPCMethod(method, name, signature, helpmsg)
        self.xmlrpcdispatcher.register_function(method, meth.name)
        self.jsonrpcdispatcher.register_function(method, meth.name)
        self.rpcmethods.append(meth)
    
