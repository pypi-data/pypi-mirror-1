"""
request dispatcher
"""

from webob import Request, exc

class TheSlasher(object):

    ### class level variables
    def __init__(self, app):
        self.app = app

    ### methods dealing with HTTP
    def __call__(self, environ, start_response):
        
        request = Request(environ)

        if request.path_info.endswith('/') and (request.path_info != '/'):
            location = request.path_info.rstrip('/')
            return exc.HTTPMovedPermanently(location=location)(environ, start_response)

        return self.app(environ, start_response)
