# -*- coding: utf-8 -*-

import argparse
import logging

import cherrypy.wsgiserver
from django.conf import settings
import django.core.handlers.wsgi
from djboss.commands import *

from djcherry.wsgi import WSGILogger


DEFAULTS = {
    'interface': getattr(settings, 'DEFAULT_CHERRY_INTERFACE', '127.0.0.1'),
    'port': getattr(settings, 'DEFAULT_CHERRY_PORT', 8080),
    'socket': getattr(settings, 'DEFAULT_CHERRY_SOCKET', None),
    'min_threads': getattr(settings, 'DEFAULT_CHERRY_MIN_THREADS', 10),
    'max_threads': getattr(settings, 'DEFAULT_CHERRY_MAX_THREADS', -1),
    'logger': getattr(settings, 'DEFAULT_CHERRY_LOGGER', 'django.cherry'),
}


@command(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
@argument('-i', '--interface', default=DEFAULTS['interface'],
    help="A TCP network interface to listen on")
@argument('-p', '--port', default=DEFAULTS['port'], type=int,
    help="A TCP port number to listen on")
@argument('-s', '--socket', default=DEFAULTS['socket'],
    help="The path to a UNIX socket to listen on. Overrides --interface/--port.")
@argument('-t', '--min-threads', default=DEFAULTS['min_threads'], type=int,
    help="The minimum number of threads to use")
@argument('-m', '--max-threads', default=DEFAULTS['max_threads'], type=int,
    help="The maximum number of threads to use. -1 means no limit.")
@argument('-l', '--logger', default=DEFAULTS['logger'],
    help="The name of the logger to use")
def cherry(clargs):    
    logger = logging.getLogger(clargs.logger)
    django_app = django.core.handlers.wsgi.WSGIHandler()
    application = WSGILogger(logger, django_app)
    
    if clargs.socket:
        bind = clargs.socket
        description = 'unix://' + clargs.socket
    else:
        bind = (clargs.interface, clargs.port)
        description = 'http://%s:%s/' % bind
    args = [bind, application]
    kwargs = {'numthreads': clargs.min_threads, 'max': clargs.max_threads}
    
    server = cherrypy.wsgiserver.CherryPyWSGIServer(*args, **kwargs)
    try:
        logger.info('Starting server on %s' % (description,))
        server.start()
    except KeyboardInterrupt:
        logger.info('Received SIGINT, shutting down gracefully')
    finally:
        logger.info('Shutting down server')
        server.stop()
        logger.info('Server shut down successfully')
