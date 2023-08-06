#coding:utf-8
from myconf import config

from os.path import join
from mypy import mypyconfig
#模板渲染的查找函数
mypyconfig.LOOKUP = dict(
    directories=join(config.PREFIX, 'mysite/htm'),
    module_directory=join(config.PREFIX, 'tmp/htm'),
    disable_unicode=True,
    encoding_errors="ignore",
    default_filters=['str', 'h'],
    filesystem_checks=config.MAKO_FILESYSTEM_CHECK
)
mypyconfig.FUNC_MODULE_PREFIX_LEN = len("mysite.ctrl.")


if config.THREAD_SAFE:
    import threading
    mypyconfig.LOCAL = threading.local()

from mypy.route_render import _ROUTE
from mypy.http_exc import Http404
from mypy import render
import mysite.ctrl

#初始化url route
_ROUTE._install(mysite.ctrl, "mysite.ctrl")

def application(request):
    render.LOCAL.request = request
    uri = request.uri
    try:
        result = _ROUTE << uri.path
    except Http404:
        result = "HTTPNotFound: %s"%(uri.path)
    except Exception:
        import traceback
        traceback.print_exc()
        raise
    return str(result)

from mypy.profile_middleware import ProfileMiddleware
application = ProfileMiddleware(application)


from mypy.gzip import GzipMiddleware
application = GzipMiddleware(application)

from mypy.yaro import Yaro, Response
application = Yaro(application)

try:
    if config.DEBUG:
        from weberror.evalexception import EvalException
        application = EvalException(application, )
    else:
        from weberror.errormiddleware import ErrorMiddleware
        application = ErrorMiddleware(application, debug=True)
except ImportError:
    import traceback
    traceback.print_exc()

from mysite.model import init_db

