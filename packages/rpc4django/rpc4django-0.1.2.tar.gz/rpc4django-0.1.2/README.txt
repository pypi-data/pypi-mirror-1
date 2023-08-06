.. Please see the full HTML documentation in the docs/ directory.
..
.. This documentation is used to generate the HTML documentation using the docutils command:
.. > rst2html.py --title="RPC4Django Documentation" --initial-header-level=2 README.txt > docs/index.html

========================
RPC4Django Documentation
========================

Version: 0.1.2

13 July 2009

.. contents:: **Table of Contents**

Overview
========

Website
-------
- http://www.davidfischer.name/rpc4django

Contributors
------------
- `David Fischer <mailto:rpc4django@gmail.com>`_

Features
--------
RPC4Django is an XMLRPC and JSONRPC application for Django powered projects. Simply plug it into any existing Django project and you can make your methods available via XMLRPC and JSONRPC. In addition, it can display nice documentation about the methods it makes available in a more customizable way than DocXMLRPCServer. 

- Detects request type (JSONRPC or XMLRPC) based on content
- Easy identification of RPC methods via a decorator
- Pure python and requires no external modules except Django
- Customizable RPC method documentation including `reST <http://docutils.sourceforge.net/rst.html>`_
- Supports XMLRPC and JSONRPC introspection
- Supports method signatures (unlike SimpleXMLRPCServer)
- Easy installation and integration with existing Django projects
- Licensed for inclusion in open source and commercial software

----

.. include:: LICENSE.txt

----

.. include:: INSTALL.txt

----

Additional Information and Settings
===================================

Running the Unit Tests
----------------------

The unit tests can be `run <http://docs.djangoproject.com/en/dev/topics/testing/#id1>`_ using ``manage.py``

::

	$> python manage.py test rpc4django

How RPC4Django Handles Requests
-------------------------------

- If the request is a GET request, return an HTML method summary
- A POST request with content-type header set to ``text/xml`` or ``application/xml`` will be processed as XMLRPC
- A POST request with content-type header containing ``json`` or ``javascript`` will be processed as JSONRPC
- Try to parse the POST data as xml. If it parses successfully, process it as XMLRPC
- Process it as JSONRPC


Method Summary
------------------------------

- The method summary displays docstrings, signatures, and names from methods marked with the ``@rpcmethod`` decorator.
- The method summary allows testing of methods via JSONRPC (unless it is disabled)
- The summary is served (unless it is disabled) from a template ``rpc4django/rpcmethod_summary.html`` and can be customized in a similar way to the `django admin <http://docs.djangoproject.com/en/dev/intro/tutorial02/#customize-the-admin-look-and-feel>`_. 
- The method summary supports `reST <http://docutils.sourceforge.net/rst.html>`_ in docstrings if the docutils library is installed. Plain text is used otherwise. Warnings and errors are not reported in the output.

Optional Settings
-----------------

These are settings that can go in your project's ``settings.py``:

``RPC4DJANGO_LOG_REQUESTS_RESPONSES=True|False`` (default True)
    By default RPC4Django will log (using the python logging module) all requests and responses. This can be disabled by setting ``RPC4DJANGO_LOG_REQUESTS_RESPONSES=False``.
``RPC4DJANGO_RESTRICT_INTROSPECTION=True|False`` (default False)
    By default RPC4Django registers the standard XMLRPC and JSONRPC introspection functions. This can be disabled by setting ``RPC4DJANGO_RESTRICT_INTROSPECTION=True``.
``RPC4DJANGO_RESTRICT_JSONRPC=True|False`` (default False)
    If ``RPC4DJANGO_RESTRICT_JSONRPC=True``, RPC4Django will never serve a JSONRPC request. Instead, either XMLRPC will be tried or status code 404 will be returned.
``RPC4DJANGO_RESTRICT_XMLRPC=True|False`` (default False)
    If ``RPC4DJANGO_RESTRICT_XMLRPC=True``, RPC4Django will never serve an XMLRPC request. Instead, either JSONRPC will be tried or status code 404 will be returned.
``RPC4DJANGO_RESTRICT_DOCUMENTATION=True|False`` (default False)
    If ``RPC4DJANGO_RESTRICT_DOCUMENTATION=True``, status code 404 will be returned instead of serving the method summary as a response to a GET request.
``RPC4DJANGO_RESTRICT_RPCTEST=True|False`` (default False)
    If ``RPC4DJANGO_RESTRICT_RPCTEST=True``, the method summary will not allow testing via JSONRPC.

----

.. include:: TODO.txt

----

.. include:: CHANGELOG.txt

