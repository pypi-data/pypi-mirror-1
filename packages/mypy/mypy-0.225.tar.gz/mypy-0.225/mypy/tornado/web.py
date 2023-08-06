#!/usr/bin/env python
#
# Copyright 2009 Facebook
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""The Tornado web framework.

The Tornado web framework looks a bit like web.py (http://webpy.org/) or
Google's webapp (http://code.google.com/appengine/docs/python/tools/webapp/),
but with additional tools and optimizations to take advantage of the
Tornado non-blocking web server and tools.

Here is the canonical "Hello, world" example app:

    import tornado.httpserver
    import tornado.ioloop
    import tornado.web

    class MainHandler(tornado.web.RequestHandler):
        def get(self):
            self.write("Hello, world")

    if __name__ == "__main__":
        application = tornado.web.Application([
            (r"/", MainHandler),
        ])
        http_server = tornado.httpserver.HTTPServer(application)
        http_server.listen(8888)
        tornado.ioloop.IOLoop.instance().start()

See the Tornado walkthrough on GitHub for more details and a good
getting started guide.
"""

import calendar
import datetime
import email.utils
import escape
import functools
import hashlib
import httplib
import logging
import os.path
import re


class RequestHandler(object):
    """Subclass this class and define get() or post() to make a handler."""

    def __init__(self, application, request, transforms=None):
        self.application = application
        self.request = request
        self._headers_written = False
        self._finished = False
        self._auto_finish = True
        self._transforms = transforms or []
        self.clear()
    """
    def head(self, *args, **kwargs):
        raise HTTPError(405)

    def get(self, *args, **kwargs):
        raise HTTPError(405)

    def post(self, *args, **kwargs):
        raise HTTPError(405)

    def delete(self, *args, **kwargs):
        raise HTTPError(405)

    def put(self, *args, **kwargs):
        raise HTTPError(405)
    """

    def prepare(self):
        """Called before the actual handler method.

        Useful to override in a handler if you want a common bottleneck for
        all of your requests.
        """
        pass

    def clear(self):
        """Resets all headers and content for this response."""
        self._headers = {
            #"Server": "TornadoServer/0.1",
            "Content-Type": "text/html; charset=UTF-8",
        }
        if not self.request.supports_http_1_1():
            if self.request.headers.get("Connection") == "Keep-Alive":
                self.set_header("Connection", "Keep-Alive")
        self._write_buffer = []
        self._status_code = 200

    def set_status(self, status_code):
        """Sets the status code for our response."""
        assert status_code in httplib.responses
        self._status_code = status_code

    def set_header(self, name, value):
        """Sets the given response header name and value.

        If a datetime is given, we automatically format it according to the
        HTTP specification. If the value is not a string, we convert it to
        a string. All header values are then encoded as UTF-8.
        """
        if isinstance(value, datetime.datetime):
            t = calendar.timegm(value.utctimetuple())
            value = email.utils.formatdate(t, localtime=False, usegmt=True)
        elif isinstance(value, int) or isinstance(value, long):
            value = str(value)
        else:
            value = str(value)
            # If \n is allowed into the header, it is possible to inject
            # additional headers or split the request. Also cap length to
            # prevent obviously erroneous values.
            safe_value = re.sub(r"[\x00-\x1f]", " ", value)[:4000]
            if safe_value != value:
                raise ValueError("Unsafe header value %r", value)
        self._headers[name] = value


    def write(self, chunk):
        """Writes the given chunk to the output buffer.

        To write the output to the network, use the flush() method below.

        If the given chunk is a dictionary, we write it as JSON and set
        the Content-Type of the response to be text/javascript.
        """
        assert not self._finished
        if isinstance(chunk, dict):
            chunk = escape.json_encode(chunk)
            self.set_header("Content-Type", "text/javascript; charset=UTF-8")
        self._write_buffer.append(chunk)


    def flush(self, include_footers=False):
        """Flushes the current output buffer to the nextwork."""
        if not self._headers_written:
            self._headers_written = True
            headers = self._generate_headers()
        else:
            headers = ""

        # Ignore the chunk and only write the headers for HEAD requests
        if self.request.method == "HEAD":
            if headers: self.request.write(headers)
            return

        if self._write_buffer:
            chunk = "".join(self._write_buffer)
            self._write_buffer = []
        else:
            chunk = ""

        if headers or chunk:
            self.request.write(headers + chunk)

    def finish(self, chunk=None):
        """Finishes this response, ending the HTTP request."""
        assert not self._finished
        if chunk: self.write(chunk)

        # Automatically support ETags and add the Content-Length header if
        # we have not flushed any content yet.
        if not self._headers_written:
            if self._status_code == 200 and self.request.method == "GET":
                hasher = hashlib.sha1()
                for part in self._write_buffer:
                    hasher.update(part)
                etag = '"%s"' % hasher.hexdigest()
                inm = self.request.headers.get("If-None-Match")
                if inm and inm.find(etag) != -1:
                    self._write_buffer = []
                    self.set_status(304)
                else:
                    self.set_header("Etag", etag)
            if "Content-Length" not in self._headers:
                content_length = sum(len(part) for part in self._write_buffer)
                self.set_header("Content-Length", content_length)

        self.flush(include_footers=True)
        self.request.finish()
        self._log()
        self._finished = True

    def send_error(self, status_code=500):
        """Sends the given HTTP error code to the browser.

        We also send the error HTML for the given error code as returned by
        get_error_html. Override that method if you want custom error pages
        for your application.
        """
        if self._headers_written:
            logging.error("Cannot send error response after headers written")
            if not self._finished:
                self.finish()
            return
        self.clear()
        self.set_status(status_code)
        message = self.get_error_html(status_code)
        self.finish(message)

    def get_error_html(self, status_code):
        """Override to implement custom error pages."""
        return "<html><title>%(code)d: %(message)s</title>" \
               "<body>%(code)d: %(message)s</body></html>" % {
            "code": status_code,
            "message": httplib.responses[status_code],
        }



    def async_callback(self, callback, *args, **kwargs):
        """Wrap callbacks with this if they are used on asynchronous requests.

        Catches exceptions and properly finishes the request.
        """
        if callback is None:
            return None
        if args or kwargs:
            callback = functools.partial(callback, *args, **kwargs)
        def wrapper(*args, **kwargs):
            try:
                return callback(*args, **kwargs)
            except Exception, e:
                if self._headers_written:
                    logging.error("Exception after headers written",
                                  exc_info=True)
                else:
                    self._handle_request_exception(e)
        return wrapper


    def _execute(self, *args, **kwargs):
        try:
            self.prepare()
            if not self._finished:  
                getattr(self, self.request.method.lower())(*args, **kwargs)
                if self._auto_finish and not self._finished:
                    self.finish()
        except Exception, e:
            self._handle_request_exception(e)

    def _generate_headers(self):
        headers = self._headers
        lines = [self.request.version + " " + str(self._status_code) + " " +
                 httplib.responses[self._status_code]]
        lines.extend(["%s: %s" % (n, v) for n, v in self._headers.iteritems()])
        return "\r\n".join(lines) + "\r\n\r\n"

    def _log(self):
        if self._status_code < 400:
            log_method = logging.info
        elif self._status_code < 500:
            log_method = logging.warning
        else:
            log_method = logging.error
        request_time = 1000.0 * self.request.request_time()
        log_method("%d %s %.2fms", self._status_code,
                   self._request_summary(), request_time)

    def _request_summary(self):
        return self.request.method + " " + self.request.uri + " (" + \
            self.request.remote_ip + ")"

    def _handle_request_exception(self, e):
        logging.error("Uncaught exception %s\n%r", self._request_summary(),
                      self.request, exc_info=e)
        self.send_error(500)


def asynchronous(method):
    """Wrap request handler methods with this if they are asynchronous.

    If this decorator is given, the response is not finished when the
    method returns. It is up to the request handler to call self.finish()
    to finish the HTTP request. Without this decorator, the request is
    automatically finished when the get() or post() method returns.

       class MyRequestHandler(web.RequestHandler):
           @web.asynchronous
           def get(self):
              http = httpclient.AsyncHTTPClient()
              http.fetch("http://friendfeed.com/", self._on_download)

           def _on_download(self, response):
              self.write("Downloaded!")
              self.finish()

    """
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if self.application._wsgi:
            raise Exception("@asynchronous is not supported for WSGI apps")
        self._auto_finish = False
        return method(self, *args, **kwargs)
    return wrapper



class Application(object):
    """A collection of request handlers that make up a web application.

    Instances of this class are callable and can be passed directly to
    HTTPServer to serve the application:

        application = web.Application([
            (r"/", MainPageHandler),
        ])
        http_server = httpserver.HTTPServer(application)
        http_server.listen(8080)
        ioloop.IOLoop.instance().start()

    """
    def __init__(self, handler):
        self.handlers = []
        self.handler = handler

    
    def __call__(self, request):
        """Called by HTTPServer to execute the request."""
        handler_class, app = self.handler
        handler = handler_class(self,request,app)
        handler._execute()
        return handler


