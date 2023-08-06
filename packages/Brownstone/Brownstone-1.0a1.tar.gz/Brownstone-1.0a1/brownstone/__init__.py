import formencode
import jinja2
import os
import os.path as paths
import re
import types
from jinja2 import Environment, FileSystemLoader

from brownstone.ctrl import Response, UrgentResponse

def erroneous(func):
    """A decorator that takes :class:`formencode.Invalid` and
    :mod:`sqlalchemy.exc` and turns them into user-friendly error
    magic."""

    def helper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except formencode.Invalid, e:
            if not hasattr(e, 'fallback'):
                raise

            self.sess['errors'] = e.unpack_errors()
            self.sess['data']   = self.req.params
            self.sess.save()
            self.redirect(e.fallback)
        except UrgentResponse, e:
            return e.resp

    helper.__name__ = func.__name__
    helper.__doc__  = func.__doc__
    return helper

def compile(routes):
    """Put routes through re.compile for performance."""

    return [(re.compile(r + '$'), klass, erroneous(method))
            for r, klass, method in routes]

def load_config(path):
    """Loads the configuration from the :file:`config.py` file in the
    same directory as this file and places it into
    :mod:`browstone.config`."""

    if not os.path.exists(path):
        raise Exception('Unable to load the configuration from "%s". Check that it exists and has the right permissions.' % path)

    config = types.ModuleType('config')
    config.__file__ = os.path.abspath(path)

    f = open(config.__file__, 'r')
    exec f in config.__dict__
    f.close()

    # Post-processing: re.compile the URLs.
    config.urls = compile(config.urls)

    # Post-processing: load the Jinja environment.
    path = paths.join(config.here, u'templates')
    config.jinja_env = \
        Environment(loader=FileSystemLoader(path),
                    undefined=jinja2.StrictUndefined,
                    autoescape=True)

    import brownstone
    brownstone.config = config
