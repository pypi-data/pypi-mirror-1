LOOKUP = None
FUNC_MODULE_PREFIX_LEN = None

import threading
_LOCAL = threading.local()
_LOCAL.request = None

from types import FunctionType
from byteplay import Code, opmap

from hmako.template import Template
from decorator import decorator


def get_request():
    return _LOCAL.request

class StringLikeObj(str): 
    def __nonzero__(self):
        return False 
 
class Gobj(object): 
    def __init__(self,template=None):
        self.template = template
        
    def __getattr__(self,name): 
        return StringLikeObj(name) 

    def __call__(self,**kwds):
        return LOOKUP.get_template(self.template).render(G=self,**kwds)

def _transmute(opcode, arg):
    if (
        (opcode == opmap['LOAD_GLOBAL']) and
        (arg == 'G' or arg == 'request')
    ):
        return opmap['LOAD_FAST'], arg
    return opcode, arg

def render_para_func(func):
    code = Code.from_code(func.func_code)
    code.args = tuple(['request','G'] + list(code.args))
    code.code = [_transmute(op, arg) for op, arg in code.code]
    func.func_code = code.to_code()
    return func


def render_func(func):
    template = "%s/%s.htm"%(
        func.__module__[FUNC_MODULE_PREFIX_LEN:].replace(".", "/"),
        func.__name__
    )
    def  _wrap_func(func,*args, **kwds):
        G=Gobj(template)
        request = get_request()
        r = func(request,G,*args, **kwds)

        if type(r) is str:
            return r
        else:
            return G(request=request)

    f = decorator(_wrap_func, func)
    
    func = render_para_func(func)

    return f


def render_doc(func):
    template = Template(
        func.__doc__,
        input_encoding='utf-8',
        output_encoding='utf-8',
        disable_unicode=True,
        default_filters=['str', 'h']
    )

    def _func(func, *args, **kwds):
        request = get_request()
        G=Gobj()

        r = func(request,G,*args, **kwds)

        if type(r) is str:
            return r
        else:
            return template.render(G=G,request=request)

    f = decorator(_func, func)
    
    func = render_para_func(func)
    
    return f

if __name__ == "__main__":

    @render_doc
    def test():
        """
        my name is ${G.x}
        request is ${request}
        %if G.not_existxxxx:
        xxx
        %else:
            ${G.not_existxxxx}
        %endif
        """
        G.x="zsp<"

    print test()