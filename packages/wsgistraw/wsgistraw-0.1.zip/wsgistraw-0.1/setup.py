#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Andrey Nordin <http://claimid.com/anrienord>"

from setuptools import setup, find_packages

setup(name="wsgistraw",
      version="0.1",
      packages = [],
      py_modules=["wsgistraw"],
      
      # Metadata for PyPI
      description="Decorators for WSGI without start_response and write",
      long_description="""\
        wsgistraw is a tiny Python library that simplifies coding WSGI applications
        and middleware by removing start_response and write from signatures of
        functions. This leads to a signature like:
        
        ::
        
        def app(environ):
        return "200 OK", [("Content-Type", "text/plain")], ["Hello World!"]
        
        That is, return a three-tuple of (status, headers, response).
        
        start_response and write are very annoying in WSGI middleware. wsgistraw makes
        your middleware code cleaner. This is an example of a "lowercase" middleware
        factory:
        
        ::
        
        @wsgistraw.mid_factory
        def lowercase(app):
        def mid(environ):
        status, headers, response = app(environ)
        return status, headers, (s.lower() for s in response)
        return mid
        
        See also:
        
        * `WSGI 2.0 at WSGI Wiki`__
        * `PEP 333`__
        
        __ http://www.wsgi.org/wsgi/WSGI_2.0
        __ http://www.python.org/dev/peps/pep-0333/""",
      author="Andrey Nordin",
      url="http://abstracthack.wordpress.com/wsgistraw",
      license="GNU LGPL",
      keywords="wsgi decorator start_response write",
      classifiers=["Environment :: Web Environment",
                   "Intended Audience :: Developers",
                   "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
                   "Operating System :: OS Independent",
                   "Programming Language :: Python",
                   "Topic :: Software Development :: Libraries",
                   "Topic :: Internet :: WWW/HTTP :: WSGI",
                   ]
)

