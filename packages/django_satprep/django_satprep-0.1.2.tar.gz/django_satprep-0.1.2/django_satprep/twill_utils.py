from nose.tools import *
from twill import add_wsgi_intercept

from django.conf import settings


DEFAULT_TWILL_PORT = 9876

TWILL_PORT = getattr(settings, 'TWILL_WSGI_PORT', DEFAULT_TWILL_PORT)
TWILL_HOST = '127.0.0.1'

TWILL_HOME = '%s:%s' % (TWILL_HOST, TWILL_PORT)

def setup():
    from django.core.servers.basehttp import AdminMediaHandler
    from django.core.handlers.wsgi import WSGIHandler
    app = AdminMediaHandler(WSGIHandler())
    add_wsgi_intercept(TWILL_HOST, TWILL_PORT, lambda: app)

