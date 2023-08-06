#coding:utf-8

from os.path import abspath,dirname,join,normpath
import sys

#初始化python的查找路径
PREFIX = normpath(dirname(dirname(dirname(abspath(__file__)))))
if PREFIX not in sys.path:
    sys.path=[PREFIX] + sys.path

from sqlbean.db.sqlstore import SqlStore
from myconf.config import DATABASE_CONFIG

SQLSTORE = SqlStore(db_config=DATABASE_CONFIG, **{})

def get_db_by_table(table_name):
    return SQLSTORE.get_db_by_table(table_name)


from sqlbean.db import connection
connection.get_db_by_table = get_db_by_table


from sqlbean.shortcut import Query,mc,MMcCache,McCache,ForeignKey,OneToMany,Model,McModel,transaction
