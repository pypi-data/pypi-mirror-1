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
from rpcdispatcher import RPCDispatcher

# these restrictions can change the functionality of rpc4django
# but they are completely optional
# see the rpc4django documentation for more details
log_requests_responses = getattr(settings,
                                 'RPC4DJANGO_LOG_REQUESTS_RESPONSES', True)
restrict_introspection = getattr(settings,
                                 'RPC4DJANGO_RESTRICT_INTROSPECTION', False)
restrict_json = getattr(settings, 'RPC4DJANGO_RESTRICT_JSONRPC', False)
restrict_xml = getattr(settings, 'RPC4DJANGO_RESTRICT_XMLRPC', False)
restrict_documentation = getattr(settings,
                                 'RPC4DJANGO_RESTRICT_DOCUMENTATION', False)
restrict_rpctest = getattr(settings, 'RPC4DJANGO_RESTRICT_RPCTEST', False)

# get a list of the installed django applications
# these will be scanned for @rpcmethod decorators
apps = getattr(settings, 'INSTALLED_APPS', [])

# instantiate the rpcdispatcher -- this examines the INSTALLED_APPS
# for any @rpcmethod decorators and adds them to the callable methods
dispatcher = RPCDispatcher(apps, restrict_introspection) 
    

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
    content_type = request.META['CONTENT_TYPE']

    if request.method == "POST" and len(request.POST) > 0:
        if log_requests_responses:
            logging.debug('Incoming request: %s' %str(request.raw_post_data))
            
        if content_type == 'text/xml' or content_type == 'application/xml':
            if restrict_xml:
                raise Http404
            
            resp = dispatcher.xmldispatch(request.raw_post_data)
            response_type = 'text/xml'
        elif content_type.find('json') >= 0 or \
             content_type.find('javascript') >= 0:
            if restrict_json:
                raise Http404
            
            resp = dispatcher.jsondispatch(request.raw_post_data)
            response_type = 'application/json'
        else:
            if log_requests_responses:
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
            if is_xml and restrict_xml:
                raise Http404
            elif not is_xml and restrict_json:
                raise Http404
            elif is_xml:
                resp = dispatcher.xmldispatch(request.raw_post_data)
                response_type = 'text/xml'
            else:
                resp = dispatcher.jsondispatch(request.raw_post_data)
                response_type = 'application/json'
            
        if log_requests_responses:
            logging.debug('Outgoing %s response: %s' %(response_type, resp))
        
        return HttpResponse(resp, response_type)
    else:
        if restrict_documentation:
            # hide the documentation by raising 404
            raise Http404
        
        # show documentation
        methods = dispatcher.list_methods()
        c = {
            'methods': methods,
            
            # restricts the ability to test the rpc server from the docs
            'restrict_rpctest': restrict_rpctest,
        }
        return render_to_response('rpc4django/rpcmethod_summary.html', c)
