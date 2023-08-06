#!/usr/bin/env python
#coding:utf-8
import subprocess
from os.path import dirname, abspath , join
import sys

PREFIX = dirname(abspath(__file__))
sys.path = [dirname(dirname(PREFIX))]+sys.path

from myconf.config import DATABASE_CONFIG
COMM_OPTION = " -h%s -P%s -u%s -p%s %s "
def backup_table(host, port, name, user, password):
    comm_option = COMM_OPTION%(host, port, user, password, name)

    """
    备份一个表数据的命令实例
    mysqldump --skip-opt --no-create-info 数据库名字 表名 --where="id<2000"
    """
    create_table_option = "--no-data --default-character-set=utf8 --skip-opt --add-drop-table --create-options --quick "+comm_option

    cmd = "mysqldump "+create_table_option
    print cmd

    with open(join(PREFIX, "table.sql"), "w") as backfile:
        subprocess.Popen(
            cmd.split(),
            stdout=backfile
        )


for key, value in DATABASE_CONFIG.iteritems():
    host, port, name, user, password = value.get("master").split(":")
    backup_table(host, port, name, user, password)


"""
create_table_option = comm_option +  "--skip-opt --no-create-info hao123"

cmd = "mysqldump "+create_table_option
print cmd

with open("data.sql", "w") as backfile:
    subprocess.Popen(
        cmd.split(),
        stdout=backfile
    )
"""
