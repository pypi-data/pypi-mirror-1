#coding:utf-8


try:
    from myconf import MERGE_CSS_JS
except:
    MERGE_CSS_JS = False

try:
    from myconf import FILE_HOST
except:
    FILE_HOST = ""

if MERGE_CSS_JS:

    my = "/css/my.css"

else:

    my = "%s/css/1~my.css"%FILE_HOST
