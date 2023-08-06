from init_app import application
from mypy.wsgiserver import CherryPyWSGIServer as WsgiServer
from myconf import config

if config.SERVER_STATIC_FILE:
    from mypy import static
    from os.path import join
    import re
    
    STATIC_VERSION = re.compile("/\d+?~")
    STATIC_FILE = static.Cling(join(config.PREFIX,"myfile"))
    STATIC_PATH = ('/css/','/js/','/pic/','/fs/','/favicon.ico','/bazs.cert')
    def url_selector(func):
        def _url_selector(environ, start_response):
            path = environ['PATH_INFO']
            for i in STATIC_PATH:
                if path.startswith(i):
                    if i in ('/css/','/js/'):
                        environ['PATH_INFO']=STATIC_VERSION.sub("/.",path)
                    return STATIC_FILE(environ, start_response)

            return func(environ, start_response)
        return _url_selector

    application = url_selector(application)

def run(host='0.0.0.0',port=9888):
    print "server on port %s"%port
    server = WsgiServer((host,port),application,numthreads=10)
    server.start()

if __name__=="__main__":
    run(port=9888)
