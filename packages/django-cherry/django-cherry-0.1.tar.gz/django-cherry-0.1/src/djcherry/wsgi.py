# -*- coding: utf-8 -*-

from django.core.handlers.wsgi import WSGIRequest


class WSGILogger(object):
    
    """Wrap a WSGI application with a process that logs"""
    
    def __init__(self, logger, application):
        self.logger = logger
        self.application = application
    
    def __call__(self, environ, start_response):
        request = WSGIRequest(environ)
        request_info = '"%s %s %s"' % (
            request.method,
            request.get_full_path(),
            request.META['SERVER_PROTOCOL'])
        
        def start_response_wrapper(status, headers):
            log = self.logger.error
            if status[0] in '23':
                log = self.logger.debug
            
            message = '%s %s %s' % (
                request_info,
                status.split()[0],
                str(get_header(headers, 'content-length') or '-'))
            log(message)
            
            return start_response(status, headers)
        
        return self.application(environ, start_response_wrapper)


def get_header(headers, header_name, default=None):
    """Get a header from a list of `(header, value)` pairs."""
    
    for header, value in headers:
        if header.lower() == header_name.lower():
            return value
    return default
