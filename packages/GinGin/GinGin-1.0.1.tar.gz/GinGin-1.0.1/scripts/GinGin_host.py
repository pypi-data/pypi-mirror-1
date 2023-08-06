#!python
import imp
import sys
import os
from os import path
from shutil import copytree, copy
import sqlite3

try:
    pkg_dir = imp.find_module('GinGin')[1]
except:
    printf >>sys.stderr, 'Can not locate module \'GinGin\'.'
    sys.exit(1)
    pass

data_dir = path.join(pkg_dir, 'data')

js_dir = path.join(data_dir, 'js')
copytree(js_dir, 'js')

images_dir = path.join(data_dir, 'images')
copytree(images_dir, 'images')

def cpdatafile(src, dst=None):
    fn = path.join(data_dir, src)
    if not dst:
        dst = src
        pass
    copy(fn, dst)
    pass

cpdatafile(path.join('css', 'GinGin_classic.css'), 'GinGin.css')
cpdatafile('GinGin_CGI.py', 'GinGin_CGI.py')
cpdatafile('GinGin_CGI.py', 'GinGin_CGI_s.py')
cpdatafile('GinGin_CGI.py', 'GinGin_TB.py')
cpdatafile('GinGin_show_doc_src.txt',)
cpdatafile('add_url.html')
cpdatafile('dot.htaccess', '.htaccess')
os.mkdir('attaches')
cpdatafile('attaches-dot.htaccess', path.join('attaches', '.htaccess'))
file('passwd', 'w+')
cpdatafile('config.py.example', 'config.py')

sql_sch = path.join(data_dir, 'GinGin.sql')
sql_sch_fo = file(sql_sch, 'r')
sql_cmds = sql_sch_fo.read()
sql_sch_fo.close()
cx = sqlite3.connect('GinGin.db')
cu = cx.cursor()
for cmd in sql_cmds.split(';\n\n'):
    cu.execute(cmd.lstrip())
    pass
cx.commit()
cx.close()

print '''
Please make sure your WEB server running with permissions to
 1. execute scripts in this directory (GinGin_CGI.py and GinGin_TB.py),
 2. read and write database 'GinGin.db',
 3. read and write this directory '%s', and
 4. read and write subdirctory 'attaches/'.
''' % (os.getcwd())

