#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# wsgistraw -- decorators for WSGI without start_response and write
# Copyright (C) 2007 Andrey Nordin
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 
# 02110-1301 USA

"""decorators for WSGI without start_response and write

wsgistraw is a tiny Python library that simplifies coding WSGI applications
and middleware by removing start_response and write from signatures of
functions. This leads to a signature like:

def app(environ):
    return "200 OK", [("Content-Type", "text/plain")], ["Hello World!"]

That is, return a three-tuple of (status, headers, response).

Project site: http://abstracthack.wordpress.com/wsgistraw

See also:

* http://www.wsgi.org/wsgi/WSGI_2.0
* http://www.python.org/dev/peps/pep-0333/ 
"""

__all__ = ["mid_factory", "app"]
__author__ = "Andrey Nordin <http://claimid.com/anrienord>"
__version__ = "0.1"

import types

def app(app):
    """Decorates WSGI application callables (both functions and methods)."""
    def decorator(*args):
        if len(args) == 2:
            environ, start_response = args
            status, headers, response = app(environ)
        elif len(args) == 3:
            self, environ, start_response = args
            status, headers, response = app(self, environ)
        else:
            raise TypeError("app() takes 2 or 3 arguments (%d given)" % len(args))
        start_response(status, headers)
        return response
    return decorator

def mid_factory(mid_factory):
    """Decorates WSGI middleware factories, i. e. callables that accept a WSGI
    application as their first positional parameter and return a middleware
    callable."""
    def decorator(app, *args, **kwargs):
        return _mid_proxy(mid_factory, app, *args, **kwargs)
    return decorator

class _mid_proxy(object):
    def __init__(self, mid_factory, app, *args, **kwargs):
        self.middleware = mid_factory(_app_proxy(app), *args, **kwargs)
        
    def __call__(self, environ, start_response):
        status, headers, response = self.middleware(environ)
        start_response(status, headers)
        return response

class _app_proxy(object):
    def __init__(self, app):
        self.app = app
        
    def __call__(self, environ):
        headers = []
        r = []
        def write(data):
            r.append(data)
        def start_response(status, response_headers, exc_info=None):
            if exc_info:
                try:
                    raise exc_info[0], exc_info[1], exc_info[2]
                finally:
                    exc_info = None
            headers[:] = [status, response_headers]
            return write
        response = self.app(environ, start_response) 
        if r:
            r.extend(r)
            response = r
        return (headers[0], headers[1], response)

