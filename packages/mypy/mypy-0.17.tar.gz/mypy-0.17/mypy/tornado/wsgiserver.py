"""HTTPServer extension to run WSGI applications. http://amix.dk/blog/viewEntry/19472"""
try:
    import cStringIO as StringIO
except:
    import StringIO

import sys
import urllib

import web
import httpserver
import ioloop


class WSGIServer(httpserver.HTTPServer):
    """HTTP Server to work with wsgi applications."""
    def __init__(self, port, wsgi_app):
        application = web.Application(
            (WSGIHandler, wsgi_app)
        )
        httpserver.HTTPServer.__init__(self, application)
        self.listen(port)

    def start(self):
        ioloop.IOLoop.instance().start()        

class WSGIHandler(web.RequestHandler):
    def __init__(self, application, request, wsgi_app):
        self.wsgi_app = wsgi_app
        web.RequestHandler.__init__(self, application, request)

    def delegate(self):
        env = self.make_wsgi_environ(self.request)
        out = self.wsgi_app(env, self._start_response)

        if not (hasattr(out, 'next') or isinstance(out, list)):
            out = [out]

        # don't send any data for redirects
        if self._status_code not in [301, 302, 303, 304, 307]:
            for x in out:
                self.write(x)

    get = post = put = delete = delegate

    def _start_response(self, status, headers, exc_info=None):
        status_code = int(status.split()[0])
        self.set_status(status_code)
        for name, value in headers:
            self.set_header(name, value)

    def make_wsgi_environ(self, request):
        """Makes wsgi environment using HTTPRequest"""
        env = {}
        env['REQUEST_METHOD'] = request.method
        env['SCRIPT_NAME'] = ""
        env['PATH_INFO'] = urllib.unquote(request.path)
        env['QUERY_STRING'] = request.query

        special = ['CONTENT_LENGTH', 'CONTENT_TYPE']

        for k, v in request.headers.items():
            k =  k.upper().replace('-', '_')
            if k not in special:
                k = 'HTTP_' + k
            env[k] = v

        env["wsgi.url_scheme"] = request.protocol
        env['REMOTE_ADDR'] = request.remote_ip
        env['HTTP_HOST'] = request.host
        env['SERVER_PROTOCOL'] = request.version

        if request.body:
            env['wsgi.input'] = StringIO.StringIO(request.body)

        env['wsgi.errors'] = sys.stderr
        env['wsgi.multithread'] = False
        env['wsgi.multiprocess'] = False
        env['wsgi.run_once'] = False

        return env


class SocketLocalMiddleware:
    """WSGI middleware to setup socket-local for request handling socket-thread."""
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, env, start_response):
        ioloop.IOLoop().instance().get_current_thread().local = {}
        return self.wsgi_app(env, start_response)


