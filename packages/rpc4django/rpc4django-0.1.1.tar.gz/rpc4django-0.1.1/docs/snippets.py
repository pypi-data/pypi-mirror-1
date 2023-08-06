# These snippets of code are run through pygmentize
# to create the nice html formatted code snippets in 
# the documentation.
#
# $> pygmentize -f html snippets.py





# urls.py
#...
urlpatterns = patterns('',    
#...
    # if installed via no install method
    #(r'^RPC2$', 'YOURPROJECT.rpc4django.views.serve_rpc_request'),
    
    # if installed via source or easy_install
    (r'^RPC2$', 'rpc4django.views.serve_rpc_request'),
)








# settings.py
#...
INSTALLED_APPS = (
#...
    # if installed via no install
    #'YOURPROJECT.rpc4django',

    # if installed via source or easy_install
    'rpc4django',
)







# testapp/__init__.py
from rpc4django import rpcmethod

# This imports another method to be made available as an RPC method
# This method should also have the @rpcmethod decorator
# from mymodule import myrpcmethod

@rpcmethod(name='mynamespace.add', signature=['int', 'int', 'int'])
def add(a, b):
    '''Adds two numbers together

    >>> add(1, 2)
    3
    '''
    return a+b
