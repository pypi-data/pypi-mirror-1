#!/usr/bin/env python

""":mod:`brownstone.wsgi`: Handles the WSGI application creation,
middleware, error pages, and routing."""

# Author: Hao Lian
# License: See license.txt

import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

import re
import os
import types
import webob
from beaker.middleware import SessionMiddleware
from webob.exc import HTTPException
from wsgiref.simple_server import make_server

from brownstone import config
from brownstone.ctrl import Response

class ErrorPage(Response):
    """A standard 404 controller."""

    def get(self, req, matches):
        """For /favicon.ico and anything else that dares stand in our
        way."""

        self.status = 404

def route(url, routes):
    """Given WSGI's path info, finds the right class and returns it
    along with any and all regexp group captures against that URL it
    found. A poor man's URL routing. See above for regular
    expressions."""

    for pattern, klass, method in routes:
        matches = pattern.match(url)
        if not matches:
            continue

        return klass, method, matches.groups()
    return ErrorPage, ErrorPage.get, tuple()

def application(env, start):
    """The WSGI__ application. For more information on WSGI, visit the
    link.

    __ http://www.python.org/dev/peps/pep-0333/"""

    # Make the environ dictionary all pretty with WebOb.
    req = webob.Request(env)

    # Find the right response object.
    klass, method, matches = route(req.path_info, config.urls)

    # Construct the object, passing the request and matches.
    try:
        req.sess = env['beaker.session']
        res = klass(req, matches, config)
        method(res, req, matches)

    # If instead of returning a response, the client threw it
    # (redirects for example), accept it dutifully.
    except HTTPException, e:
        return e(env, start)

    # Send HTTP status and HTTP headers the WebOb way.
    start(res.status, res.headerlist)

    # Send the HTTP body, live happily ever after.
    return [res.body]

application = SessionMiddleware(application, config.beaker)

def loop():
    """A little WSGI server based on :mod:`wsgiref` and the magic of
    :class:`KeyboardInterrupt`. Handles Ctrl-C gracefully. Runs on
    `port 8000`__.

    __ http://localhost:8000/"""

    try:
        httpd = make_server('', config.port, application)
        print(u'Now running on localhost:%d' % config.port)
        httpd.serve_forever()
    except KeyboardInterrupt:
        print(u'Shutting down')
        httpd.server_close()

if __name__ == '__main__':
    loop()
