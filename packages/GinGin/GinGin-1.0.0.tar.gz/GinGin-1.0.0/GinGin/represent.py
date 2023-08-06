#!evn python
import sys
from config import *
from string import join
from html_template import *
import tools

def error_page(msg, ofo):
    from templates import error_page
    from xml_template import escape_cdata
    data = {}
    data['host'] = GINGIN_SITE
    data['error'] = msg
    data['title'] = ''
    error_page.str = tools.hack_str
    return data, error_page.error_page(ofo), None

def redirect(url, msg):
    print 'Status: 307 Temporary Redirect'
    print 'Location: %s' % (url)
    print 'Content-Type: text/html; charset=' + GINGIN_ENCODING
    print
    print '<html><body>%s</body><html>' % (msg)


def show_update_ok(doc_id, title, spath):
    from xml_template import escape_cdata
    title = title.decode('utf8').encode(GINGIN_ENCODING)
    print 'Location: %s?func=show_id_doc&doc_id=%d' % (spath, doc_id)
    print 'Content-Type: text/html; charset=' + GINGIN_ENCODING
    print
    print '<html><body>%s</body></html>' % (escape_cdata(title),)


def show_update_url_ok(url_id, url, abstract, title, keyword):
    from xml_template import escape_cdata
    keyword = escape_cdata(keyword.decode('utf8').encode(GINGIN_ENCODING))
    title = title.decode('utf8').encode(GINGIN_ENCODING)
    url = escape_cdata(url.decode('utf8').encode(GINGIN_ENCODING))
    print 'Location: GinGin_CGI_s.py?func=show_kw_urls&keyword=%s' % (keyword)
    print 'Content-Type: text/html; charset=' + GINGIN_ENCODING
    print
    print '<html><body>%s - %s</body></html>' % (title, url)


def show_del_kw_urls_ok(keyword, url_ids):
    from xml_template import escape_cdata
    keyword = keyword.decode('utf8').encode(GINGIN_ENCODING)
    print 'Location: GinGin_CGI_s.py/show_kw_urls/%s' % (keyword)
    print 'Content-Type: text/html; charset=' + GINGIN_ENCODING
    print
    print '<html><body>%s</body></html>' % (escape_cdata(keyword),)


def show_doc(kws, doc_id, title, doc_body, pdate, creator, comments=None):
    from xml_template import escape_cdata, escape_url
    kws = [escape_cdata(kw) for kw in kws]
    title = escape_cdata(title)
    doc_body = escape_cdata(doc_body)
    doc = {'id': doc_id, 'title': title, 'body': doc_body, 'date': pdate, 'creator': creator, 'keywords': {'key':kws}}
    out = {'doc': doc}
    if comments:
	comments = [{'cmt_id': c[0], 'name': escape_cdata(c[1]), 'email': escape_cdata(c[2]), 'website': escape_url(c[3]), 'msg': escape_cdata(c[4]), 'pdate': c[5]} for c in comments]
	doc['comments'] = {'comment': comments}
	pass
    return out


def show_doc_src(kws, doc_id, title, doc_body, pdate, creator):
    skws = join(kws, ';').encode(GINGIN_ENCODING)
    title = title.encode(GINGIN_ENCODING)
    doc_body = doc_body.encode(GINGIN_ENCODING)
    data = {'encoding': GINGIN_ENCODING, 'keywords': skws, 'doc_id': `doc_id`, 'title': title, 'doc_body': doc_body, 'pdate': pdate.encode(GINGIN_ENCODING), 'creator': creator.encode(GINGIN_ENCODING)}
    jdata = {}
    print 'Content-Type: text/plain; charset=' + GINGIN_ENCODING
    print
    format_template(GINGIN_SHOW_DOC_SRC, data, jdata)


def edit_doc(kws, doc_id, title, doc_body, pdate, creator):
    from xml_template import escape_cdata
    kws = [escape_cdata(kw) for kw in kws]
    title = escape_cdata(title)
    doc_body = escape_cdata(doc_body)
    out = {'edit': {'title': title, 'keywords': {'key': kws}, 'id': doc_id, 'body': doc_body, 'date': pdate, 'creator': creator}}
    return out


def show_docs_of_kw(keyword, docs, urls):
    from xml_template import escape_cdata, escape_url
    docs = map(lambda x: {'id': x[1], 'title': escape_cdata(x[2]), 'date': x[4], 'creator': x[5]}, docs) # doc_id, title, pdate, creator
    urls = map(lambda x: {'id': x[0], 'title': escape_cdata(x[1]), 'url': escape_url(x[2]), 'abstract': escape_cdata(x[3]), 'date': x[4], 'creator': x[5]}, urls)
    out = {}
    out['keyword'] = {'name': escape_cdata(keyword), 'docs': {'doc': docs}, 'urls': {'url': urls}}
    return out


def show_all_kws(kws):
    from xml_template import escape_cdata
    kws = [escape_cdata(kw) for kw in kws]
    out = {'keywords': {'key': kws}}
    return out


def show_afkeys_doc(doc_id, afkeys):
    out = {'doc': {'attaches': {'attach': afkeys}, 'id': doc_id}}
    return out
    

def show_deny(user, task, doc_id):
    print 'Content-Type: text/html; charset=' + GINGIN_ENCODING
    print
    print '<html><body>Permission Deny!</body></html>'
    return


def send_file(fname, asfname, mtype):
    from sys import stdout
    from os import stat
    from time import asctime, gmtime
    
    st = stat(fname)
    st_mtime = asctime(gmtime(st[8])) + ' GMT'
    print 'Content-Type: ' + mtype + '; name="' + asfname + '"'
    print 'Content-Disposition: attachment; filename="' + asfname + '"'
    print 'Last-Modified: ' + st_mtime
    print
    fo = open(fname, 'r')
    buf = fo.read(10240)
    while len(buf):
	stdout.write(buf)
	buf = fo.read(10240)
    return

def not_found(name):
    from xml_template import escape_cdata
    print 'Content-Type: text/plain'
    print 'Status: 404 not found'
    print
    print '404 Not found'
    print escape_cdata(name) + ' is not found!'
    print 'By GinGin.'
    return

def go_back(env):
    from xml_template import escape_url
    refer = env['HTTP_REFERER']
    refer = escape_url(refer)
    print 'Location: ' + refer
    print 'Content-Type: text/html; charset=' + GINGIN_ENCODING
    print
    print 'Move to ' + refer
    return

def show_edit_comment(doc_id, attack):
    plain = attack[1]
    cipher = attack[2]
    
    out = {'comment': {'doc_id': doc_id, 'attack': {'plain': plain, 'cipher': cipher}}}
    return out

def show_last_comments(comments):
    from tools import list_pair_to_pairs_list
    from xml_template import escape_cdata, escape_url
    comments = [(c[0], c[1], escape_cdata(c[2]), escape_cdata(c[3]), escape_url(c[4]), escape_cdata(c[5]), c[6]) for c in comments]
    fnames = ('cmt_id', 'doc_id', 'name', 'email', 'website', 'msg', 'pdate')
    d_comments = [dict(list_pair_to_pairs_list(fnames, comment)) for comment in comments]
    out = {'comments': {'comment': d_comments}}
    return out

def show_to_robot(docs, env):
    import tools
    base, spath = tools.get_server_url(env)
    print 'Content-Type: text/html'
    print
    print '<html><body>'
    for doc_id in docs:
	print '<a href="%s/show_id_doc/%d">%d</a>' % (spath, doc_id, doc_id)
    print '</body></html>'
    return

def show_rssfeed(abstracts):
    from xml_template import escape_cdata
    abstracts = map(lambda x: { 'doc_id': x[0], 'title': escape_cdata(x[1]), 'pdate': x[2], 'creator': x[3], 'abs': escape_cdata(x[4])}, abstracts)
    out = { 'feeds': { 'feed': abstracts}}
    return out

def show_kw_urls(keyword, urls):
    from xml_template import escape_cdata, escape_url
    keyword = escape_cdata(keyword)
    urls = map(lambda x: {'id': x[0], 'title': escape_cdata(x[1]), 'url': escape_url(x[2]), 'abstracts': [{'abstract': escape_cdata(x[3])}], 'date': x[4], 'creator': x[5]}, urls)
    out = { 'name': keyword, 'urls': urls, 'url_cnt': len(urls)}
    return out

def show_edit_url(url, kws):
    from xml_template import escape_cdata, escape_url
    kws = [escape_cdata(kw) for kw in kws]
    x = url
    url = {'id': url[0], 'title': escape_cdata(url[1]), 'url': escape_url(x[2]), 'abstract': escape_cdata(x[3]), 'date': x[4], 'creator': x[5]}
    url['keywords'] = {'key': kws}
    out = {'edit': {'url': url}}
    return out
