#!/usr/bin/env python
#coding:utf-8
from __future__ import with_statement
from os.path import dirname, join, abspath, basename
import subprocess
from os import makedirs
from os.path import exists
from hashlib import md5
from os import walk
from glob import glob
from struct import unpack
from zlib import crc32
from shutil  import copyfile
from struct import pack
from base64 import urlsafe_b64encode


prefix = dirname(abspath(__file__))
merge_prefix = prefix

def walk_filter(basedir, dirfilter=None, filefilter=None):
    for dirpath, dirnames, filenames in walk(basedir):
        if dirfilter and not dirfilter(dirpath):
            continue
        prefix = dirpath[len(basedir)+1:]
        for filename in filenames:
            if filefilter and not filefilter(filename):
                continue
            yield join(prefix, filename)

class ChangeFilter():
    def __init__(self, buffer_file):
        self.filename2num = dict()
        self.filename2hash = dict()
        self.buffer_file = buffer_file
        self.salt = ""

    def __call__(self, basedir, filelist):
        buffer_file = self.buffer_file
        if exists(buffer_file):
            init_py = open(buffer_file)
            hash_lines = [
                i.strip() for i in
                list(init_py)
            ]
            hash_lines = [
                i for i in hash_lines if i
            ]
            init_py.close()
        else:
            hash_lines = []

        if hash_lines:
            self.salt = hash_lines[0]
            hash_lines = hash_lines[1:]
        else:

            from os import urandom
            self.salt = urlsafe_b64encode(urandom(3))[:3]


        for i in hash_lines:
            hash, num, filename = i.split()
            self.filename2hash[filename] = hash
            self.filename2num[filename] = int(num)

        for i in filelist:
            with open(join(basedir, i)) as inf:
                hash = md5(inf.read()).hexdigest()
                result = self.filename2hash.get(i)
                if result == hash:
                    continue
                if result is None:
                    self.filename2num[i] = 1
                else:
                    self.filename2num[i] += 1
                self.filename2hash[i] = hash
                yield i

    def flush(self):
        with open(self.buffer_file, "w") as inf:
            inf.write("%s\n"%self.salt)
            for filename, hash in self.filename2hash.iteritems():
                inf.write(
                    "%s\t%s\t%s\n"%(hash, self.filename2num[filename], filename)
                )

def merge(subdir, template):
    file_hash_version = ChangeFilter(
        join(prefix, ".%s_hash"%subdir)
    )
    subdir = join(prefix, subdir)
    for i in file_hash_version(
        subdir,
        walk_filter(subdir, lambda x:x.find(".svn")==-1, lambda x:(x.endswith(".css") or x.endswith(".js")) and not x.startswith("."))
    ):
        infile = join(subdir, i)
        bi = basename(i)
        outfile = join(subdir, i[:-len(bi)]+"."+bi)
        filetype = "css"
        if infile.endswith(".js"):
            filetype = "js"
        cmd = [
                "java", "-jar", join(prefix, "yuicompressor.jar"), "--charset=utf-8", "--type", filetype, infile, "-o", outfile
        ]
        try:
            returncode = subprocess.call(cmd)
            if returncode:
                raise
        except:
            file_hash_version.filename2num[i] -= 1
            file_hash_version.filename2hash[i] = "0"
            print "yuicompressor error : %s"%infile
            copyfile(infile, outfile)
    file_hash_version.flush()
    from mako.template import Template
    init_template = Template(template)
    init_py_file = join(subdir, "__init__.py")
    with open(init_py_file, "w") as init_py:
        filenum = file_hash_version.filename2num.iteritems()
        init_py.write(
            "#coding:utf-8\n\n"+init_template.render(
                filename2num=dict(
                    (
                        k,
                         "%s%s"%(
                            file_hash_version.salt,
                            urlsafe_b64encode(
                                pack("Q", v).rstrip("\x00")
                            ).rstrip("=")
                        )
                    )
                    for k, v in
                    file_hash_version.filename2num.iteritems()
                )
            )
        )

JS_INIT_TEMPLATE = """\
<%!
from os.path import join,basename,dirname
%>
try:
    from myconf.config import ORG_CSS_JS
except:
    ORG_CSS_JS = False

try:
    from myconf.config import JS_FILE_HOST
except:
    JS_FILE_HOST = ""

if ORG_CSS_JS:
%for path,num in filename2num.iteritems():
<%
path = path.rsplit(".js",1)[0]
name = path.replace("/","_").replace(".","_")
%>
    ${name} = "/js/${path}.js"
%endfor

else:
%for path,num in filename2num.iteritems():
<%
path = path.rsplit(".js",1)[0]
name = path.replace("/","_").replace(".","_")
pathdir = join("js",dirname(path))
pathfile = basename(path)
filename = join(pathdir,"%s~%s.js"%(num,pathfile)).replace("\\\\","/")
%>
    ${name} = "%s/${filename}"%JS_FILE_HOST
%endfor
"""


CSS_INIT_TEMPLATE = """\
<%!
from os.path import join,basename,dirname
%>
try:
    from myconf.config import ORG_CSS_JS
except:
    ORG_CSS_JS = False

try:
    from myconf.config import FILE_HOST
except:
    FILE_HOST = ""

if ORG_CSS_JS:
%for path,num in filename2num.iteritems():
<%
path = path.rsplit(".css",1)[0]
name = path.replace("/","_").replace(".","_")
%>
    ${name} = "/css/${path}.css"
%endfor

else:
%for path,num in filename2num.iteritems():
<%
path = path.rsplit(".css",1)[0]
name = path.replace("/","_").replace(".","_")
pathdir = join("css",dirname(path))
pathfile = basename(path)
filename = join(pathdir,"%s~%s.css"%(num,pathfile)).replace("\\\\","/")
%>
    ${name} = "%s/${filename}"%FILE_HOST
%endfor
"""
merge("css", CSS_INIT_TEMPLATE)
print "CSS Merge Game Over"

merge("js", JS_INIT_TEMPLATE)
print "JS Merge Game Over"
