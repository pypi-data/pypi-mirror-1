#coding:utf-8

from os.path import abspath, dirname, join, normpath
import sys

#初始化python的查找路径
PREFIX = normpath(dirname(dirname(dirname(abspath(__file__)))))
if PREFIX not in sys.path:
    sys.path = [PREFIX] + sys.path


from myconf.config import MEMCACHED_ADDR, DISABLE_LOCAL_CACHED
from sqlbean.db.mc_connection import init_mc
init_mc(memcached_addr=MEMCACHED_ADDR, disable_local_cached=DISABLE_LOCAL_CACHED)


from myconf.config import DATABASE_CONFIG, THREAD_SAFE
from sqlbean.db import connection
connection.THREAD_SAFE = THREAD_SAFE

from sqlbean.db import sqlstore
SQLSTORE = sqlstore.SqlStore(db_config=DATABASE_CONFIG, **{})
def get_db_by_table(table_name):
    return SQLSTORE.get_db_by_table(table_name)
connection.get_db_by_table = get_db_by_table

from sqlbean.shortcut import Query, mc, McCacheM, McCache, ForeignKey, OneToMany, Model, McModel


