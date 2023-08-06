# -*- coding: utf-8 -*-

"""makes django to log all 500 to defined error log"""

from django.conf import settings
from django.utils.importlib import import_module
from django.http import HttpResponseServerError
from django.template import Context, RequestContext, loader
import logging, sys


logger = logging.getLogger('TRUELOGGING')
logger.propogate = False
logger.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s - Unhandled'
                              ' Exception at %(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)


def server_error(request, template_name='500.html'):
    """copy of default server_error, but with logging"""
    logger.exception('%s\n', request.path)
    t = loader.get_template(template_name)
    return HttpResponseServerError(t.render(Context({})))


# we patch default urlconf if it uses default django 500 handler
urlconf = import_module(settings.ROOT_URLCONF)
if urlconf.handler500 == 'django.views.defaults.server_error':
    urlconf.handler500 = 'truelogging.server_error'