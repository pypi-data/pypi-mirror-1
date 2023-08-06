from distutils.core import setup

charset = 'big5'

class fake_file(object):
    pass

def trans_templates():
    import os
    from os import path
    try:
        from mez_xml import mez_xml
    except:
        import sys
        print >>sys.stderr, 'Please install mez_xml before running setup.py.'
        sys.exit(1)
        pass
    
    temp_dir = path.join('temp_src', charset)
    fns = [fn for fn in os.listdir(temp_dir) if fn.endswith('.temp')]
    for fn in fns:
        temp = path.join(temp_dir, fn)
        pytemp = path.join('GinGin', 'templates', fn[:-5] + '.py')
                                        # s/.temp$/.py/
        ifo = file(temp, 'r')
        ofo = file(pytemp, 'w+')
        fake_ifo = fake_file()
        fake_ifo.read = lambda x=None: ifo.read(x).decode(charset).encode('utf8')
        fake_ofo = fake_file()
        fake_ofo.write = lambda x: ofo.write(x.encode(charset))
        print >>ofo, '# -*-: %s' % (charset)
        mx = mez_xml.mez_xml()
        mx.start(fn, fake_ifo, fake_ofo)
        pass
    pass

trans_templates()

setup(name='GinGin',
      version='1.0.0',
      packages=['GinGin', 'GinGin.templates'],
      package_data={'GinGin': ['data/GinGin.sql',
                               'data/GinGin_CGI.py',
                               'data/GinGin_show_doc_src.txt',
                               'data/add_url.html',
                               'data/dot.htaccess',
                               'data/attaches-dot.htaccess',
                               'data/config.py.example',
                               'data/css/*.css',
                               'data/images/GinGin.svg',
                               'data/images/*/*.jpg',
                               'data/js/*.js']},
      scripts=['scripts/GinGin_host.py'],
      requires=['mez_xml', '_sqlite3', 'fcgi'],
      author='Thinker K.F. Li',
      author_email='thinker@branda.to',
      url='http://trac-hg.assembla.com/GinGin/',
      description='GinGin is a hybrid of WIKI and BLOG system.',
      long_description='''
GinGin is a hybrid of WIKI and BLOG.  Users of GinGin can setup tags for
their documents.  The documents will be hyper-linked, automatically, when
tags are in the content of them.  In another word, GinGin will create
cross-reference for documents by the tags specified by users.

GinGin also has capability to tag URLs.  URLs are associated with tags
and cross-referenced for documents.
      ''',
      classifiers=['Programming Language :: Python',
                   'License :: OSI Approved :: BSD License',
                   'Natural Language :: Chinese (Traditional)',
                   'Topic :: Communications'],
      )
