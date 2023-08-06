'''
Views

This module contains the method serve_rpc_request which is intended to
be called from the urls.py module of a 
`django <http://www.djangoproject.com/>`_ project.

It should be called like this from urls.py:

    (r'^RPC2$', 'rpc4django.views.serve_rpc_request'),

'''

import logging
from xml.dom.minidom import parseString
from xml.parsers.expat import ExpatError
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
from django.conf import settings
from django.core.urlresolvers import reverse, NoReverseMatch
from rpcdispatcher import RPCDispatcher
from __init__ import version

# these restrictions can change the functionality of rpc4django
# but they are completely optional
# see the rpc4django documentation for more details
LOG_REQUESTS_RESPONSES = getattr(settings,
                                 'RPC4DJANGO_LOG_REQUESTS_RESPONSES', True)
RESTRICT_INTROSPECTION = getattr(settings,
                                 'RPC4DJANGO_RESTRICT_INTROSPECTION', False)
RESTRICT_JSON = getattr(settings, 'RPC4DJANGO_RESTRICT_JSONRPC', False)
RESTRICT_XML = getattr(settings, 'RPC4DJANGO_RESTRICT_XMLRPC', False)
RESTRICT_METHOD_SUMMARY = getattr(settings, 
                                  'RPC4DJANGO_RESTRICT_METHOD_SUMMARY', False)
RESTRICT_RPCTEST = getattr(settings, 'RPC4DJANGO_RESTRICT_RPCTEST', False)

# get a list of the installed django applications
# these will be scanned for @rpcmethod decorators
APPS = getattr(settings, 'INSTALLED_APPS', [])
    

def serve_rpc_request(request):
    '''
    This method handles rpc calls based on the content type of the request
    
    It dispatches based on the following rules:
    
    1. If there is no post data, display documentation
    2. content-type = text/xml or application/xml => XMLRPC
    3. content-type contains json or javascript => JSONRPC
    4. Try to parse as xml. Successful parse => XMLRPC
    5. JSONRPC
    '''
    

    if request.method == "POST" and len(request.POST) > 0:
        # Handle POST request with RPC payload
        
        content_type = request.META.get('CONTENT_TYPE', 'unknown type')
        
        if LOG_REQUESTS_RESPONSES:
            logging.debug('Incoming "%s" request: %s' \
                          %(content_type, str(request.raw_post_data)))
            
        if content_type == 'text/xml' or content_type == 'application/xml':
            if RESTRICT_XML:
                raise Http404
            
            resp = dispatcher.xmldispatch(request.raw_post_data)
            response_type = 'text/xml'
        elif content_type.find('json') >= 0 or \
             content_type.find('javascript') >= 0:
            if RESTRICT_JSON:
                raise Http404
            
            resp = dispatcher.jsondispatch(request.raw_post_data)
            response_type = 'application/json'
        else:
            if LOG_REQUESTS_RESPONSES:
                logging.info('Unrecognized content-type "%s"' %content_type)
                logging.info('Analyzing rpc request data to get content type')
                
            # analyze post data to see whether it is xml or json
            # this is slower than if the content-type was set properly
            try:
                parseString(request.raw_post_data)
                is_xml = True
            except ExpatError:
                is_xml = False

            # deal with the data based on what it is
            if is_xml and RESTRICT_XML:
                raise Http404
            elif not is_xml and RESTRICT_JSON:
                raise Http404
            elif is_xml:
                resp = dispatcher.xmldispatch(request.raw_post_data)
                response_type = 'text/xml'
            else:
                resp = dispatcher.jsondispatch(request.raw_post_data)
                response_type = 'application/json'
            
        if LOG_REQUESTS_RESPONSES:
            logging.debug('Outgoing %s response: %s' %(response_type, resp))
        
        return HttpResponse(resp, response_type)
    else:
        # Handle GET request
        
        if RESTRICT_METHOD_SUMMARY:
            # hide the documentation by raising 404
            raise Http404
        
        # show documentation
        methods = dispatcher.list_methods()
        template_data = {
            'methods': methods,
            'url': URL,
            
            # rpc4django version
            'version': version(),
            
            # restricts the ability to test the rpc server from the docs
            'restrict_rpctest': RESTRICT_RPCTEST,
        }
        return render_to_response('rpc4django/rpcmethod_summary.html', \
                                  template_data)

# reverse the method for use with system.describe and ajax
try:
    URL = reverse(serve_rpc_request)
except NoReverseMatch:
    URL = ''
    
# instantiate the rpcdispatcher -- this examines the INSTALLED_APPS
# for any @rpcmethod decorators and adds them to the callable methods
dispatcher = RPCDispatcher(URL, APPS, RESTRICT_INTROSPECTION) 
