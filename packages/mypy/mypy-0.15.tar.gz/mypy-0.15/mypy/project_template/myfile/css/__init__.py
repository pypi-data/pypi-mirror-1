#coding:utf-8


try:
    from myconf.config import ORG_CSS_JS
except:
    ORG_CSS_JS = False

try:
    from myconf.config import FILE_HOST
except:
    FILE_HOST = ""

if ORG_CSS_JS:

    my = "/css/my.css"

else:

    my = "%s/css/1~my.css"%FILE_HOST
