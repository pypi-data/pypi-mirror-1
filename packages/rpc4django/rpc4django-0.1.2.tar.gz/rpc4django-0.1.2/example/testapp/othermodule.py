from rpc4django import rpcmethod

@rpcmethod(name='myns.broken')
def broken(a):
 '''
 Broken contains erroneous markup *@#$(*&#(U<>M><M<>M><M>M><
   and un
  expected
 indentation

 .. and comments

 ./././*( and other markup
 '''
 return "successful call"