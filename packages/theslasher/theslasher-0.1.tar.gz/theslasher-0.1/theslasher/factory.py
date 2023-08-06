from paste.httpexceptions import HTTPExceptionHandler
from theslasher import TheSlasher
from webob import Response

def example(environ, start_response):
    return Response(content_type='text/plain', body=environ['PATH_INFO'])(environ, start_response)

def factory(global_conf, **app_conf):
    """create a webob view and wrap it in middleware"""
    return TheSlasher(example)
    
