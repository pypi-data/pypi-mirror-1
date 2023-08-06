#coding:utf-8
class Form(object):
    def __init__(self,d=None):
        if d is None:
            d = {}
        self.__dict__["_Form__d"] = d

    def __iter__(self):
        for i in self.__d.iteritems():
            yield i

    def __nonzero__(self):
        return bool(self.__d)

    def __setattr__(self,name,value):
        self.__d[name] = value

    def __getattr__(self,name):
        return self.__d.get(name,"")

    def __getitem__(self,name):
        return self.__d.get(name,"")

    def __contains__(self,b):
        return b in self.__d

    def __setitem__(self,name,val):
        self.__d[name] = val
        
    def __delitem__(self,name):
        del self.__d[name]

WHITE_SPACE = "\r\n \t¡¡"
class StripForm(object):
    def __init__(self,form):
        self.__dict__["_StripForm__f"] = form
    
    def __getattr__(self,name):
        return getattr(self.__f)

    def __getattr__(self,name):
        return self.__f[name].strip(WHITE_SPACE)
        
    def __getitem__(self,name):
        return self.__f[name].strip(WHITE_SPACE)

