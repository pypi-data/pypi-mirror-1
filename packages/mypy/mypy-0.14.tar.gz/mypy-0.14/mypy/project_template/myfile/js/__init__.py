#coding:utf-8


try:
    from myconf import MERGE_CSS_JS
except:
    MERGE_CSS_JS = False

try:
    from myconf import JS_FILE_HOST
except:
    JS_FILE_HOST = ""

if MERGE_CSS_JS:

    my = "/css/my.js"

else:

    my = "%s/js/1~my.js"%JS_FILE_HOST
