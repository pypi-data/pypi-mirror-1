#coding:utf-8
from os.path import abspath,dirname,join,normpath
import sys

#初始化python的查找路径
PREFIX = normpath(dirname(dirname(abspath(__file__))))
if PREFIX not in sys.path:
    sys.path=[PREFIX] + sys.path

#是否启用在线调试
DEBUG = True

#是否启用Mako的自动检测模板更新
MAKO_FILESYSTEM_CHECK = True

#是否python由提供静态文件的服务
SERVER_STATIC_FILE = True

#静态文件服务器的域名
FILE_HOST = ""

try:
    from local_config import *
except ImportError:
    print "WARNING : local_config not exist"