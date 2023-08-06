#coding:utf-8
from os.path import abspath, dirname, join, normpath
import sys

#初始化python的查找路径
PREFIX = normpath(dirname(dirname(abspath(__file__))))
if PREFIX not in sys.path:
    sys.path = [PREFIX] + sys.path

#数据库配置
WTREE_HOST = "localhost:3306:wtree:root:111111"
DATABASE_CONFIG = None

#是否使用多线程
THREAD_SAFE = False

#是否启用在线调试
DEBUG = True

#是否使用优化过的css，js
ORG_CSS_JS = True

#是否启用Mako的自动检测模板更新
MAKO_FILESYSTEM_CHECK = True

#是否python由提供静态文件的服务
SERVER_STATIC_FILE = True

#静态文件服务器的域名
FILE_HOST = ""

#Javascript文件服务器的域名
JS_FILE_HOST = ""

#Memcache的地址
MEMCACHED_ADDR = None
#MEMCACHED_ADDR = ["127.0.0.1:11211"]

#是否禁用进程内缓存
DISABLE_LOCAL_CACHED = False

#系统发信人的邮箱地址和显示名称
SYS_EMAIL_SENDER = "stdyun@sina.com"
SYS_EMAIL_SENDER_NAME = "stdyun"

#发信的SMTP服务器，用户名，密码
SMTP = "smtp.sina.com"
SMTP_USERNAME = "stdyun"
SMTP_PASSWORD = "xxxxxx"

try:
    from local_config import *
except ImportError:
    print "WARNING : local_config not exist"

if not DATABASE_CONFIG:
    DATABASE_CONFIG = {
        "wtree": {
            "master": WTREE_HOST,
            "tables": (
                "*",
                "user", "user_apply", "user_password", "user_email",
                "user_profile",
            ),
        },
    }

