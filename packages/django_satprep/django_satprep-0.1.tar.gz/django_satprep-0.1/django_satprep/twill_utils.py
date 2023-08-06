from nose.tools import *
from twill import add_wsgi_intercept

from django.conf import settings


DEFAULT_TWILL_PORT = 9876


def setup():
    from django.core.servers.basehttp import AdminMediaHandler
    from django.core.handlers.wsgi import WSGIHandler
    app = AdminMediaHandler(WSGIHandler())
    twill_port = getattr(settings, 'TWILL_WSGI_PORT', DEFAULT_TWILL_PORT)
    add_wsgi_intercept("127.0.0.1", twill_port, lambda: app)

