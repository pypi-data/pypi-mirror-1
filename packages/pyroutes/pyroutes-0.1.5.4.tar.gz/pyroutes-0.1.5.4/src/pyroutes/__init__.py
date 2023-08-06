#!/usr/bin/env python
#encoding: utf-8

from wsgiref.util import shift_path_info
import cgi
import sys
    
global __request__handlers__
__request__handlers__ = {}

def route(path):
    """
    Decorates a function for handling page requests to
    a certain path
    """
    global __request__handlers__
    
    def decorator(func):
        if path in __request__handlers__:
            raise ValueError("Tried to redefine handler for %s with %s" % (path, func))
        __request__handlers__[path] = func
    return decorator

def create_request_path(environ):
    """
    Returns a tuple consisting of the individual request parts
    """
    handlers = __request__handlers__.keys()
    path = shift_path_info(environ)
    request = []
    if not path:
        request = ['/']
    else:
        while path:
            request.append(path)
            path = shift_path_info(environ)
    return request

def find_request_handler(current_path):
    """
    Locates the handler for the specified path. Return None if not found.
    """
    handler = None
    while handler is None:
        if current_path in __request__handlers__:
            handler = __request__handlers__[current_path]
            break
        current_path = current_path[:current_path.rfind("/")]
        if not current_path:
            return None
    return handler

def create_data_dict(environ):
    """
    """
    _data = cgi.FieldStorage(
        fp=environ['wsgi.input'],
        environ=environ,
        keep_blank_values=False
    )
    data = {}
    for key in _data.keys():
        data[key] = _data.getvalue(key)
    return data

def application(environ, start_response):
    """
    Searches for a handler for a certain request and
    dispatches it if found. Returns 404 if not found.
    """

    request = create_request_path(environ.copy())
    complete_path = '/%s' % '/'.join(request)
    handler = find_request_handler(complete_path)
    if not handler:
        start_response('404 Not Found', [('Content-type', 'text/plain')])
        return ["No handler found for path %s" % complete_path]

    try:
        data = create_data_dict(environ)
        response = handler(environ, data)
        if 'Content-Length' not in [a[0] for a in response.headers]:
            response.headers.append(('Content-Length', str(sys.getsizeof(response.content))))
        start_response(response.status_code, response.headers)
        return [response.content]
    except Exception, exception:
        start_response('500 Error', [('Content-type', 'text/plain')])
        return ["An error occurred\n%s" % str(exception)]

