from init_app import application
from myconf import config

try:
    from mypy.tornado.wsgiserver import WSGIServer as WSGIServer
except ImportError:
    print "import tornado.wsgiserver FAILED , USE CherryPyWSGIServer INSTEAD"
    from mypy.wsgiserver import CherryPyWSGIServer as WSGIServer

if config.SERVER_STATIC_FILE:
    from mypy import static
    from os.path import join
    import re

    STATIC_VERSION = re.compile("/\d+?~")
    STATIC_FILE = static.Cling(join(config.PREFIX, "myfile"))
    STATIC_PATH = ('/css/', '/js/', '/pic/', '/fs/', '/favicon.ico', '/bazs.cert', '/robots.txt')
    def url_selector(func):
        def _url_selector(environ, start_response):
            path = environ['PATH_INFO']
            for i in STATIC_PATH:
                if path.startswith(i):
                    if i in ('/css/', '/js/'):
                        environ['PATH_INFO'] = STATIC_VERSION.sub("/.", path)
                    return STATIC_FILE(environ, start_response)

            return func(environ, start_response)
        return _url_selector

    application = url_selector(application)

def run(port=9888):
    print "server on port %s"%port
    server = WSGIServer(port, application)
    server.start()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        port = int(sys.argv[1])
    else:
        port = 9888
    run(port=port)
