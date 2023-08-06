from rpc4django import rpcmethod
from othermodule import broken

@rpcmethod(name='myns.mytestmethod',signature=['int', 'int', 'int', 'int'])
def mytestmethod(a, b, c):
 '''
 mytestmethod
 ------------

 summery
 =======

 This method tests `reST <http://docutils.sourceforge.net/rst.html>`_ markup

 Returns
   the number 42

 Parameters:

 - `a` (number)
 - `b` (number)
 - `c` (number)
 '''
 return 42

@rpcmethod(name='myns.shorty')
def shorty():
 return "short method"
