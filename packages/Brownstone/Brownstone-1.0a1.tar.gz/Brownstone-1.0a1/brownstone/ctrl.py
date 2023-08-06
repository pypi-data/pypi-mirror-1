import logging
log = logging.getLogger(__name__)

import mimetypes
import os
import os.path as paths
import random
import time
import urlparse
import webob
from formencode import htmlfill
from webob.exc import HTTPNotFound, HTTPNotModified, HTTPFound

class UrgentResponse(Exception):
    """Urgently raised for immediate HTTP output."""

    def __init__(self, resp):
        self.resp = resp

class Response(webob.Response):
    """Subclass of WebOb's response class, superclass of all of our
    response objects. Mostly tinkers with WebOb to get everything into
    Unicode."""

    def __init__(self, req, matches, config, *a, **kw):
        super(Response, self).__init__(*a, **kw)
        self.charset = req.charset = 'utf-8'

        # Jinja.
        self.jinja_env = config.jinja_env
        # WebOb request object.
        self.req = req
        # Matches in routing.
        self.matches = matches
        # Data to be passed to Jinja.
        self.base = config.base
        self.data = dict(base=self.base)
        # Beaker session.
        self.sess = req.sess
        # CSRF protection.
        if not 'nonce' in self.sess:
            self.sess['nonce'] = self.nonce()
            self.sess.save()
        # XHR.
        self.xhr = req.params.get('xhr') == u'1'

        self.init(req, matches, config)

    def init(self, req, matches, config):
        """Post-init hook."""
        pass

    @apply
    def ubody():
        doc = """I got tired of typing unicode_body."""

        def fget(self):
            return self.unicode_body

        def fset(self, value):
            self.unicode_body = value

        return property(**locals())

    def render(self, path):
        """Render Jinja template at :obj:`path` with the data in
        :attr:`self.data`. The fields user and _nonce get populated
        with the current user object and the current session nonce
        automatically if they're not already set."""

        self.data.setdefault('_nonce', self.sess['nonce'])

        template = self.jinja_env.get_template(path)
        self.ubody = template.render(**self.data)
        return self

    def fill_data(self, data):
        """Fills forms in :obj:`self.ubody` with the dictionary of
        data in :obj:`data`."""

        R = htmlfill.render
        return R(self.ubody, data, force_defaults=False)

    def fill_errors(self):
        """Fills forms in :obj:`self.ubody` with the dictionary of
        data in :obj:`data` and errors in :obj:`self.sess`. Does
        nothing but return :obj:`self` if no errors are found.
        Otherwise raises itself---a :class:`webob.Response`
        object---for immediate HTTP output by the server. Errors are
        created when a formencode exception is caught in
        :func:`brownstone.erroneous` and turned into a redirection to
        a fallback URL specified when the :meth:`to_python` method is
        called on form schemas."""

        R = htmlfill.render

        # If there are no errors, become a no-op and sadly return.
        errors = self.sess.pop('errors', None)
        if not errors:
            return self

        data = self.sess.pop('data', None)
        if not data:
            return self

        self.ubody = R(self.ubody, data, errors,
                       auto_insert_errors=False)
        self.sess.save()
        raise UrgentResponse(self)

    def redirect(self, url):
        """Raises :class:`webob.exc.HTTPFound` with the passed url."""

        url = urlparse.urljoin(self.base, url)
        raise HTTPFound(location=url)

    def stop(self, errors):
        """Takes a list of errors, renders it, and immediately returns
        the response to client."""

        self.data['errors'] = errors

        # Serialize to UTF-8 JavaScript if XHR is on.
        if self.xhr:
            self.render('errors.xhr.html')
        else:
            self.render('errors.html')

        raise UrgentResponse(self)

    def nonce(self):
        """Returns a unique token for a session. Procedure copied from
        the Pylons-family webhelpers module."""

        return random.getrandbits(128)

    def check_nonce(self):
        """Raises an error response unless the nonce in the request
        matches the nonce in the session. Raises an
        :class:`AssertionError` if there is no nonce session key.
        Otherwise returns self."""

        assert 'nonce' in self.sess
        assert 'nonce' in self.req.params

        nonce = self.req.params.get('nonce')
        if nonce.isdigit():
            nonce = int(nonce)

        # Malicious users with a non-numeric nonce will automatically
        # fail in this equality check.
        if not nonce == self.sess['nonce']:
            self.stop([u'Session expired, sorry. Return, reload, and try again.'])

        return self

class Static(Response):
    """A static file controller for CSS, JavaScript, and so forth."""

    def __init__(self, req, matches, config, *a, **kw):
        """Saves :obj:`config.here`."""

        super(Static, self).__init__(req, matches, config, *a, **kw)
        self.static_here = paths.join(config.here, 'static')

    def index(self, req, matches):
        """The only method. Writes binary data to :obj:`self.body`."""

        path = paths.join(self.static_here, matches[0])

        if not paths.isfile(path):
            raise HTTPNotFound()

        # Cache control magic.
        self.cache_expires(60 * 60 * 24)
        self.vary = ['Cookie']

        # Conditional get magic.
        self.last_modified = time.ctime(os.stat(path).st_mtime)
        if req.if_modified_since and not req.range:
            if req.if_modified_since >= self.last_modified:
                raise HTTPNotModified()

        with open(path, 'rb') as f:
            self.body = f.read()

        mime = mimetypes.guess_type(path)[0]
        self.content_type = mime or 'text/plain'
