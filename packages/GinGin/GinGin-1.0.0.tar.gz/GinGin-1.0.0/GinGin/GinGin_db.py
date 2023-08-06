#!env python
import sqlite3
import string
from config import *
from time import strftime
from sets import Set

cx = None
_WORDCHARS = string.letters + string.digits + '-_'

def now():
    return strftime('%Y-%m-%d %H:%M:%S %Z')

class GG_DB_ERR:
    def __init__(self):
	pass

def update_doc(doc_id, title, keywords, context, uid, update_pdate, published):
    global cx
    if not cx:
	cx = sqlite3.connect(GINGIN_DB)
    cu = cx.cursor()
    if doc_id < 0:
	#
	# add a new doc
	#
	cmd = 'insert into docs(title, doc_body, pdate, creator, published) values(?, ?, ?, ?, ?)'
	cu.execute(cmd, (title, context, now(), uid, published and 1 or 0))
	cu.execute('select max(doc_id) from docs')
	doc_id = int(cu.fetchone()[0])
	del_set = Set()
	add_set = Set(keywords)
    else:
	#
	# update a doc
	#
	# choice keyword sets that should be add or del
	cmd = 'select a.keyword from keywords a inner join kws_docs b on a.kw_id = b.kw_id where b.doc_id = ?'
	cu.execute(cmd, (doc_id,))
	okws = cu.fetchall()
	okws = map(lambda x: x[0], okws)
	old_set = Set(okws)
	new_set = Set(keywords)
	del_set = old_set - new_set
	add_set = new_set - old_set
	# update
	if update_pdate:
	    cmd = 'update docs set title = ?, doc_body = ?, pdate = ?, creator = ?, published = ? where doc_id = ?'
	    cu.execute(cmd, (title, context, now(), uid,
                             published and 1 or 0, doc_id))
	else:
	    cmd = 'update docs set title = ?, doc_body = ?, creator = ?, published = ? where doc_id = ?'
	    cu.execute(cmd, (title, context, uid,
                             published and 1 or 0, doc_id))
	    pass
	pass
    # remove keywords
    cmd = 'delete from kws_docs where kw_id = (select kw_id from keywords where keyword = ?) and doc_id = ?'
    try:
	while 1:
	    kw = del_set.pop()
	    if not kw:
		break
	    try:
		cu.execute(cmd, (kw, doc_id))
	    except sqlite3.DatabaseError:
		pass
    except KeyError:
	pass
    # add kws_docs
    cmd = 'insert into kws_docs select * from (select kw_id, ? from keywords where keyword = ?)'
    try:
	while 1:
	    kw = add_set.pop()
	    if not kw:
		break
	    try:
		# add keywords
		cu.execute('insert into keywords(keyword) values(?)', (kw,))
	    except sqlite3.DatabaseError:
		pass
	    cu.execute(cmd, (doc_id, kw))
    except KeyError:
	pass
    # remove useless keywords (no doc reference by it in kws_docs)
    cu.execute('delete from keywords where kw_id in (select a.kw_id from keywords a left join kws_docs b on a.kw_id = b.kw_id left join kws_urls c on a.kw_id = c.kw_id where (b.kw_id isnull) and (c.kw_id isnull))')
    cx.commit()
    return doc_id


def get_kw_docs(keyword):
    global cx
    if not cx:
	cx = sqlite3.connect(GINGIN_DB)
    cu = cx.cursor()
    # get doc with specified keyword
    cmd = 'select c.doc_id, c.title, c.pdate, c.creator from keywords as a inner join kws_docs as b on a.kw_id = b.kw_id inner join docs as c on b.doc_id = c.doc_id where a.keyword = ? and c.published = 1'
    cu.execute(cmd, (keyword,))
    docs = cu.fetchall()
    cx.commit()
    return docs


def get_kw_urls(keyword):
    global cx
    if not cx:
	cx = sqlite3.connect(GINGIN_DB)
    cu = cx.cursor()
    
    cmd = 'select a.url_id, title, url, abstract, pdate, creator from urls a join kws_urls b on a.url_id = b.url_id join keywords c on b.kw_id = c.kw_id where c.keyword = ?'
    cu.execute(cmd, (keyword,))
    urls = cu.fetchall()
    res = map(lambda x: (x[0], x[1], x[2], x[3], x[4], x[5]), urls)
    cx.commit()
    return res

def get_url(url_id):
    global cx
    if not cx:
	cx = sqlite3.connect(GINGIN_DB)
    cu = cx.cursor()
    
    cmd = 'select url_id, title, url, abstract, pdate, creator from urls where url_id = ?'
    cu.execute(cmd, (url_id,))
    url = cu.fetchone()
    url = map(lambda x: x, url) 
    
    cmd = 'select keyword from keywords a join kws_urls b on a.kw_id = b.kw_id where b.url_id = ?'
    cu.execute(cmd, (url_id,))
    kws = cu.fetchall()
    kws = map(lambda x: x[0], kws)

    cx.commit()
    return (url, kws)

def update_url(url_id, title, url, abstract, uid, kws):
    global cx
    if not cx:
	cx = sqlite3.connect(GINGIN_DB)
    cu = cx.cursor()
    
    if url_id < 0:
	cmd = 'insert into urls select max(url_id) + 1, ?, ?, ?, ?, ? from urls'
	cu.execute(cmd, (title, url, abstract, now(), uid))
	cmd = 'select max(url_id) from urls'
	cu.execute(cmd)
	url_id = int(cu.fetchone()[0])
	del_set = Set()
	add_set = Set(kws)
    else:
	cmd = 'update urls set title = ?, url = ?, abstract = ?, pdate = ?, creator = ? where url_id = ?'
	cu.execute(cmd, (title, url, abstract, now(), uid, url_id))
	cmd = 'select keyword from keywords a join kws_urls b on a.kw_id = b.kw_id where b.url_id = ?'
	cu.execute(cmd, (url_id,))
	old_kws = map(lambda x: x[0], cu.fetchall())
	old_set = Set(old_kws)
	new_set = Set(kws)
	del_set = old_set - new_set
	add_set = new_set - old_set
    # remove kws_urls being removed by the user
    cmd = 'delete from kws_urls where kw_id = (select kw_id from keywords where keyword = ?) and url_id = ?'
    try:
	while 1:
	    kw = del_set.pop()
	    if not kw:
		break
	    cu.execute(cmd, (kw, url_id))
    except KeyError:
	pass
    # add kws_urls being add by tye user
    cmd = 'insert into kws_urls select kw_id, ? from keywords where keyword = ?'
    try:
	while 1:
	    kw = add_set.pop()
	    if not kw:
		break
	    try:
		cu.execute('insert into keywords select max(kw_id) + 1, ? from keywords', (kw,))
	    except sqlite3.DatabaseError:
		pass
	    cu.execute(cmd, (url_id, kw))
    except KeyError:
	pass
    # remove useless keywords (no doc reference by it in kws_docs)
    cu.execute('delete from keywords where kw_id in (select a.kw_id from keywords a left join kws_docs b on a.kw_id = b.kw_id left join kws_urls c on a.kw_id = c.kw_id where (b.kw_id isnull) and (c.kw_id isnull))')
    cx.commit()
    return url_id

def del_kw_urls(keyword, url_ids):
    from string import join
    global cx
    if not cx:
	cx = sqlite3.connect(GINGIN_DB)
    cu = cx.cursor()
    
    url_str = join(map(lambda x: str(x), url_ids), ', ')
    cmd = 'delete from kws_urls where url_id in (' + url_str + ') and kw_id in (select kw_id from keywords where keyword = ?)'
    cu.execute(cmd, (keyword,))
    # remove useless keywords (no doc reference by it in kws_docs)
    cu.execute('delete from keywords where kw_id in (select a.kw_id from keywords a left join kws_docs b on a.kw_id = b.kw_id left join kws_urls c on a.kw_id = c.kw_id where (b.kw_id isnull) and (c.kw_id isnull))')
    # remove useless urls (no keyword reference it any more)
    cu.execute('delete from urls where url_id in (select a.url_id from urls a left join kws_urls b on a.url_id = b.url_id where b.kw_id isnull)')
    cx.commit()
    return

def get_last_docs(n):
    global cx
    if not cx:
	cx = sqlite3.connect(GINGIN_DB)
    cu = cx.cursor()
    cmd = 'select doc_id, title, pdate, creator from docs where published = 1 order by pdate desc limit ?'
    cu.execute(cmd, (n,))
    docs = cu.fetchall()
    res = map(lambda x: (x[0], x[1], x[2], x[3]), docs)
    cx.commit()
    return res

def get_unpublished_docs():
    global cx
    if not cx:
	cx = sqlite3.connect(GINGIN_DB)
    cu = cx.cursor()
    cmd = 'select doc_id, title, pdate, creator from docs where published = 0 order by pdate desc'
    cu.execute(cmd)
    docs = cu.fetchall()
    res = map(lambda x: (x[0], x[1], x[2], x[3]), docs)
    cx.commit()
    return res

def get_last_doc_ids(n):
    global cx
    if not cx:
	cx = sqlite3.connect(GINGIN_DB)
    cu = cx.cursor()
    cmd = 'select doc_id from docs where published = 1 order by doc_id desc limit ?'
    cu.execute(cmd, (n,))
    docs = cu.fetchall()
    res = map(lambda x: x[0], docs)
    cx.commit()
    return res

def abstract_document(doc):
    if len(doc) > GINGIN_ABSTRACT_SZ:
	sz = GINGIN_ABSTRACT_SZ
	while sz < len(doc):
	    if doc[sz] in string.whitespace:
		break
	    sz = sz + 1
	    pass
	doc = doc[:sz] + ' ...'
	pass
    return doc


def get_last_abstracts(n):
    global cx
    if not cx:
	cx = sqlite3.connect(GINGIN_DB)
    cu = cx.cursor()
    cmd = 'select doc_id, title, pdate, creator, doc_body from docs where published = 1 order by pdate desc limit ?'
    cu.execute(cmd, (n,))
    docs = cu.fetchall()
    res = map(lambda x: (x[0], x[1], x[2], x[3], abstract_document(x[4])), docs)
    cx.commit()
    return res


def get_id_doc(doc_id):
    global cx
    if not cx:
	cx = sqlite3.connect(GINGIN_DB)
    cu = cx.cursor()
    # get doc
    cmd = 'select * from docs where doc_id = ?'
    cu.execute(cmd, (doc_id,))
    row = cu.fetchone()
    if not row:
        raise ValueError, \
            'The document, with id #%d, is not existed.' % (doc_id)
    title = row[1]
    doc_body = row[2]
    pdate = row[3]
    creator = row[4]
    published = row[5] and True or False
    # get keywords
    cmd = 'select keyword from keywords a inner join kws_docs b on a.kw_id = b.kw_id where b.doc_id = ?'
    cu.execute(cmd, (doc_id,))
    rows = cu.fetchall()
    kws = map(lambda x: x[0], rows)
    cx.commit()
    return (kws, doc_id, title, doc_body, pdate, creator, published)


def get_id_doc_attack(doc_id, cu=None):
    global cx
    wcu = cu
    if wcu == None:
	if not cx:
	    cx = sqlite3.connect(GINGIN_DB)
	    pass
	wcu = cx.cursor()
	pass
    cmd = 'select key, plain, cipher from antispam where doc_id = ?'
    wcu.execute(cmd, (doc_id,))
    row = wcu.fetchone()
    if row:
	attack = row[0], row[1], row[2]
    else:
	import antispam, array, base64
	key = antispam.get_key(doc_id)
	plain, cipher = antispam.gen_an_attack(key)
	key = base64.b64encode(array.array('B', key).tostring())
	plain = base64.b64encode(array.array('B', plain).tostring())
	cipher = base64.b64encode(array.array('B', cipher).tostring())
	cmd = 'insert into antispam(doc_id, key, plain, cipher) values(?, ?, ?, ?)'
	wcu.execute(cmd, (doc_id, key, plain, cipher))
	attack = key, plain, cipher
        pass
    
    if cu == None:
        cx.commit()
        pass
    return attack


def get_id_doc_comments(doc_id, cu=None):
    global cx
    wcu = cu
    if wcu == None:
	if not cx:
	    cx = sqlite3.connect(GINGIN_DB)
	    pass
	wcu = cx.cursor()
	pass
    cmd = 'select cmt_id, name, email, website, msg, pdate from comments where doc_id = ?'
    wcu.execute(cmd, (doc_id,))
    rows = wcu.fetchall()
    comments = [(row[0], row[1], row[2], row[3], row[4], row[5]) for row in rows]
    if cu == None:
        cx.commit()
        pass
    return comments


def add_id_doc_comment(doc_id, name, email, website, msg, key, cu=None):
    global cx
    wcu = cu
    if wcu == None:
	if not cx:
	    cx = sqlite3.connect(GINGIN_DB)
	    pass
	wcu = cx.cursor()
	pass
    cmd = 'select * from antispam where doc_id = ? and key = ?'
    wcu.execute(cmd, (doc_id, key))
    row = wcu.fetchone()
    if not row:
	return
    if website:
	cmd = 'insert into comments (doc_id, name, email, website, msg, pdate) values(?, ?, ?, ?, ?, ?)'
	wcu.execute(cmd, (doc_id, name, email, website, msg, now()))
    else:
	cmd = 'insert into comments (doc_id, name, email, msg, pdate) values(?, ?, ?, ?, ?)'
	wcu.execute(cmd, (doc_id, name, email, msg, now()))
	pass
    if cu == None:
	cx.commit()
    pass


def get_last_comments(num=5):
    global cx
    if not cx:
	cx = sqlite3.connect(GINGIN_DB)
    cu = cx.cursor()
    
    cmd = 'select cmt_id, doc_id, name, email, website, msg, pdate from comments order by cmt_id desc limit ?'
    cu.execute(cmd, (num,))
    rows = cu.fetchall()
    comments = [tuple(row) for row in rows]
    return comments


def get_all_kws(cu=None):
    global cx
    wcu = cu
    if wcu == None:
	if not cx:
	    cx = sqlite3.connect(GINGIN_DB)
	wcu = cx.cursor()
    wcu.execute('select keyword from keywords order by keyword')
    rows = wcu.fetchall()
    if cu == None:
	cx.commit()
    kws = map(lambda x:x[0], rows)
    return kws

def _range_cmp(x, y):
    if x[0] > y[1]:
	r = 1
    elif x[1] < y[0]:
	r = -1
    else:
	r = 0
    return r

def replace_kws(msg, kws):
    import re
    
    c = lambda x, y: len(x) - len(y);
    kws.sort(c, lambda x: x, True)
    kws = map(lambda x: re.escape(x), kws)
    kw_pattern = '\\$|([hH][tT][tT][pP]|[aA][tT][tT][aA][cC][hH]):[^ ]*'
    if kws:
	kw_pattern = kw_pattern + '|' + string.join(kws, '|')
	pass
    reo_kws = re.compile(kw_pattern)
    reo_url = re.compile('([hH][tT][tT][pP]|[aA][tT][tT][aA][cC][hH]):[^ ]*')
    
    mos = reo_kws.finditer(msg)
    
    def mark(mo):
	kw = mark.msg[mo.start():mo.end()]
	if reo_url.match(kw):
	    res = mark.msg[mark.last:mo.end()]
	elif kw == '$':
	    res = mark.msg[mark.last:mo.end()] + '$'
	elif (kw[0] not in mark.en_chars) or \
	((mark.msg[mo.start()-1] not in mark.en_chars) and \
	(mark.msg[mo.end()] not in mark.en_chars)):
	    res = mark.msg[mark.last:mo.start()] + '$' + kw + '$'
	else:
	    res = msg[mark.last:mo.end()]
	mark.last = mo.end()
	return res
    # setup closures
    mark.last = 0
    mark.msg = msg
    mark.en_chars = string.ascii_letters + string.digits
    
    substrs = map(mark, mos)
    return string.join(substrs,'') + msg[mark.last:]


def exist_doc_id(doc_id, cu=None):
    global cx
    wcu = cu
    if wcu == None:
	if not cx:
	    cx = sqlite3.connect(GINGIN_DB)
	wcu = cx.cursor()
    wcu.execute('select count(*) from docs where doc_id = ?', (doc_id,))
    cnt = wcu.fetchone()[0]
    if cu == None:
	cx.commit()
    return cnt > 0


def get_afname_mtype_by_afkey(doc_id, afkey, cu=None):
    global cx
    wcu = cu
    if wcu == None:
	if not cx:
	    cx = sqlite3.connect(GINGIN_DB)
	wcu = cx.cursor()
        pass

    cmd = 'select afname, mtype from afiles where doc_id = ? and afkey = ?'
    wcu.execute(cmd, (doc_id, afkey))
    rows = wcu.fetchall()
    if len(rows) == 0:
	return None, None
    return rows[0][0], rows[0][1]


def __mk_afname(doc_id, afkey, mtype, cu=None):
    global cx
    wcu = cu
    if wcu == None:
	if not cx:
	    cx = sqlite3.connect(GINGIN_DB)
	wcu = cx.cursor()
    
    wcu.execute('select max(af_id) + 1 from afiles')
    af_id = wcu.fetchone()[0]
    if af_id == None:
	af_id = 1
    
    afname = 'attaches/af-' + `doc_id` + '-' + `af_id`
    cmd = 'insert into afiles values(?, ?, ?, ?, ?)'
    wcu.execute(cmd, (af_id, doc_id, afkey, afname, mtype))
    
    if cu == None:
	cx.commit()
    return afname

def add_afile_to_doc(doc_id, afkey, fobj, mtype):
    global cx
    if not cx:
	cx = sqlite3.connect(GINGIN_DB)
    cu = cx.cursor()
    
    # get afname
    if not exist_doc_id(doc_id):
	raise GG_DB_ERR()
    afname, o_mtype = get_afname_mtype_by_afkey(doc_id, afkey, cu)
    if afname == None:
	afname = __mk_afname(doc_id, afkey, mtype, cu)
    elif o_mtype != mtype:
	cmd = 'update afiles set mtype = ? where doc_id = ? and afkey = ?'
	cu.execute(cmd, (mtype, doc_id, afkey))
    
    cx.commit()
    
    # save attach file
    afo = open(afname, 'w+')
    buf = fobj.read(10240)
    while len(buf):
	afo.write(buf)
	buf = fobj.read(10240)
    afo.close()
    return


def remove_afile_by_afkey(doc_id, afkey, cu=None):
    global cx
    wcu = cu
    if wcu == None:
	if not cx:
	    cx = sqlite3.connect(GINGIN_DB)
	wcu = cx.cursor()
    
    afname, mtype = get_afname_mtype_by_afkey(doc_id, afkey, wcu)
    if afname == None:
	raise GG_DB_ERR()
    
    cmd = 'delete from afiles where doc_id = ? and afkey = ?'
    wcu.execute(cmd, (doc_id, afkey))
    import os
    os.remove(afname)
    
    if cu == None:
	cx.commit()
    return

def is_doc_published(doc_id, cu=None):
    global cx
    wcu = cu
    if wcu == None:
	if not cx:
	    cx = sqlite3.connect(GINGIN_DB)
	wcu = cx.cursor()
        pass
    
    cmd = 'select 1 from docs where doc_id = ? and published = 1'
    wcu.execute(cmd, (doc_id,))
    rows = wcu.fetchall()
    
    if cu == None:
        cx.commit()
        pass

    if len(rows) != 1:
        return False
    return True


def get_afkeys_doc(doc_id, cu=None):
    global cx
    wcu = cu
    if wcu == None:
	if not cx:
	    cx = sqlite3.connect(GINGIN_DB)
	wcu = cx.cursor()
        pass
    
    cmd = 'select afkey from afiles where doc_id = ?'
    wcu.execute(cmd, (doc_id,))
    rows = wcu.fetchall()
    afkeys = map(lambda x: x[0], rows)
    
    return afkeys


def get_hot_keywords(hot_n, cu=None):
    global cx
    wcu = cu
    if wcu == None:
	if not cx:
	    cx = sqlite3.connect(GINGIN_DB)
	wcu = cx.cursor()
    
    cmd = 'select * from hot_kws where num > 0 order by num desc limit ?'
    wcu.execute(cmd, (hot_n,))
    rows = wcu.fetchall()
    kws = map(lambda x: (x[0], x[1]), rows);
    
    return kws

def trackback_ping(doc_id, title, excerpt, url, blog_name, rhost, cu=None):
    global cx
    wcu = cu
    if wcu == None:
	if not cx:
	    cx = sqlite3.connect(GINGIN_DB)
	wcu = cx.cursor()
    
    cmd = 'insert into trackbacks values(?, ?, ?, ?, ?, ?, ?)'
    wcu.execute(cmd, (doc_id, title, excerpt, url, blog_name, rhost, now()))
    if cu == None:
	cx.commit()
    return

def get_trackback_pings(doc_id, cu=None):
    global cx
    wcu = cu
    if wcu == None:
	if not cx:
	    cx = sqlite3.connect(GINGIN_DB)
	wcu = cx.cursor()
    
    cmd = 'select * from trackbacks where doc_id=?'
    wcu.execute(cmd, (doc_id,))
    rows = wcu.fetchall()
    pings = map(lambda x: (x[1], x[2], x[3], x[4], x[5], x[6]), rows)
    if cu == None:
	cx.commit()
    return pings

def get_referers_of_doc(doc_id, cu=None):
    global cx
    wcu = cu
    if wcu == None:
	if not cx:
	    cx = sqlite3.connect(GINGIN_DB)
	wcu = cx.cursor()
    cmd = 'select src_url from referers where doc_id=?'
    wcu.execute(cmd, (doc_id,))
    rows = wcu.fetchall()
    referers = [x[0] for x in rows]
    if cu == None:
	cx.commit()
    return referers

def add_referer(doc_id, url, cu=None):
    global cx
    wcu = cu
    if wcu == None:
	if not cx:
	    cx = sqlite3.connect(GINGIN_DB)
	wcu = cx.cursor()
    cmd = 'insert into referers select max(ref_id)+1, ?, ? from referers'
    try:
	wcu.execute(cmd, (doc_id, url))
    except sqlite3.DatabaseError:
	pass

    if cu == None:
	cx.commit()
    pass
