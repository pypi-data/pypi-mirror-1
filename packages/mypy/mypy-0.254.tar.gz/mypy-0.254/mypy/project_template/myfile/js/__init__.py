#coding:utf-8


try:
    from myconf.config import ORG_CSS_JS
except:
    ORG_CSS_JS = False

try:
    from myconf.config import JS_FILE_HOST
except:
    JS_FILE_HOST = ""

if ORG_CSS_JS:

    my = "/js/my.js"

    reg = "/js/reg.js"

else:

    my = "%s/js/1tAg~my.js"%JS_FILE_HOST

    reg = "%s/js/1tAw~reg.js"%JS_FILE_HOST
