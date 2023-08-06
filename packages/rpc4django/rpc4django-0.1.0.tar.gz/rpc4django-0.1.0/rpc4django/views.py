'''
Views

This module contains the method serve_rpc_request which is intended to
be called from the urls.py module of a django project.

It should be called like this from urls.py:
    (r'^RPC2$', 'rpc4django.views.serve_rpc_request'),

see http://www.djangoproject.com/

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

import logging
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
    1. If there is not post data, display documentation or 404 if restricted
    2. If the content type is text/xml, dispatch to xmlrpc unless restricted
    3. If application/json, dispatch to jsonrpc unless restricted
    4. If content type contains xml, dispatch to xmlrpc unless restricted
    5. Dispatch to jsonrpc unless restricted
    6. Raise 404
    '''
    content_type = request.META['CONTENT_TYPE']

    if request.method == "POST" and len(request.POST) > 0:
        if log_requests_responses:
            logging.debug('Incoming request: %s' %str(request.raw_post_data))
            
        if content_type == 'application/json' and not restrict_json:
            resp = dispatcher.jsondispatch(request.raw_post_data)
            response_type = 'application/json'
        elif content_type == 'text/xml' and not restrict_xml:
            resp = dispatcher.xmldispatch(request.raw_post_data)
            response_type = 'text/xml'
        else:
            # try to guess the content type
            if log_requests_responses:
                logging.info('Trying to guess rpc server type from %s' \
                         %content_type)
            if content_type.find('xml') >= 0 and not restrict_xml:
                resp = dispatcher.xmldispatch(request.raw_post_data)
                response_type = 'text/xml'
            elif not restrict_json:
                resp = dispatcher.jsondispatch(request.raw_post_data)
                response_type = 'application/json'
            else:
                raise Http404
            
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
