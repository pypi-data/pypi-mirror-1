"""HTTPServer extension to run WSGI applications. http://amix.dk/blog/viewEntry/19472"""


import web
import httpserver
import ioloop
from web import WSGIHandler

class WSGIServer(httpserver.HTTPServer):
    """HTTP Server to work with wsgi applications."""
    def __init__(self, port, wsgi_app ):
        application = web.Application(
            (WSGIHandler, wsgi_app)
        )
        httpserver.HTTPServer.__init__(self, application)
        self.listen(port)

    def start(self):
        ioloop.IOLoop.instance().start()


class SocketLocalMiddleware:
    """WSGI middleware to setup socket-local for request handling socket-thread."""
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, env, start_response):
        ioloop.IOLoop().instance().get_current_thread().local = {}
        return self.wsgi_app(env, start_response)


