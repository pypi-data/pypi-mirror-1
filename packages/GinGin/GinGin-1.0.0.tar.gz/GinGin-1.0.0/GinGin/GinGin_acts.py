import os
from config import *
import GinGin_db
import represent
import types
import tools
from string import split

def mixin(cls, mixcls):
    cls.__bases__ += (mixcls,)
    pass

def get_keywords(str):
    kws = split(str, ';')
    rkws = []
    for kw in kws:
	while len(kw):
	    if kw[0] == ' ':
		kw = kw[1:]
	    elif kw[-1] == ' ':
		kw = kw[:-1]
	    else:
		break
	if len(kw):
	    rkws.append(kw)
    return rkws


def get_url_of_doc(doc_id, env):
    link = 'http://' + env['SERVER_NAME']
    if env['SERVER_PORT'] != '80':
	link = link + ':80'
    link = link + env['SCRIPT_NAME']
    last = link.rfind('/')
    link = link[:last + 1] + 'GinGin_CGI.py'
    link = link + '/show_id_doc/' + str(doc_id)
    return link


def gingin_date_to_http_date(tm):
    from time import asctime, strptime
    return asctime(strptime(tm, '%Y-%m-%d %H:%M:%S %Z'))


def gingin_date_to_rss_date(tm):
    from time import strftime, strptime, timezone
    zone = timezone
    if timezone < 0:
	zone = -zone
	sig = '-'
    else:
	sig = '+'
	pass
    zh = zone/(60*60)
    zm = (zone / 60) % 60
    zonestr = '%s%02d:%02d' % (sig, zh, zm)
    tm = strptime(tm, '%Y-%m-%d %H:%M:%S %Z')
    return strftime('%Y-%m-%dT%H:%M:%S' + zonestr, tm)


class EMPTY_ACTION:
    def __init__(self, msg):
	self.__msg = msg
	
    def __repr__(self):
	return "EMPTY_ACTION: " + self.__msg
    
    def __str__(self):
	return "EMPTY_ACTION: " + self.__msg
    pass


class DENY_ACTION:
    def __init__(self, user, act_name, doc_id):
	self.user = user
	self.act_name = act_name
	self.doc_id = doc_id
	pass
    pass

# ========================================

## \defgroup app_action_G Application Actions
#
# Every request from user client will trigger some actions to serve
# the user.  An action can as complex as performing a transaction, or
# as easy as reading a file.  All these actions are modeled as
# \ref new_action classes.  Every request will trigger a corresponding
# new_action class.  The class would be instantiated and called; it is
# a callable.
#
# \ref action_form_G are used to be mixed-in with \ref new_action to
# provide form variables. These variables are parameters provided by
# users.  new_action objects read variables and customize actions for
# users.
#
# \ref new_octr_G controls output stream of new_action objects.
# new_action objects can specify Content-Type or other headers
# and tell \ref new_octr_G how to generate the output from data provided by
# new_action objects.

## An new_action is a callable that performs application actions.
# \ingroup app_action_G
#
# New_action is abstraction of actions of GinGin.
# Every WEB requestion from user client triggers a new_action
# to perform actions.
#
# A new_action is a callable that being called to perform actions.
class new_action(object):
    def __init__(self, act_name, ival=[], fval=[]):
	super(new_action, self).__init__()
	self._act_name = act_name
	self._ival = ival
        self._fval = fval
	self.encoding = GINGIN_ENCODING
	pass

    ## Authorize the user to access a document.
    #
    # \param doc_id is ID of the document be authorized.
    # \return User ID.
    #
    # If doc_id is -1, it is authorized for an action
    # that is not for any document.
    def auth(self, doc_id=-1):
	user = GINGIN_USER.get_login_user(self.octr)
	if not GINGIN_USER.authorize(self, user, self._act_name, doc_id):
	    raise DENY_ACTION(user, self._act_name, doc_id)
	return user

    ## Conventional function for transcoding locale string to UTF8.
    def to_utf8(self, data, enc=None):
	if enc == None:
	    enc = self.encoding
	return data.decode(enc).encode('utf8')

    ## Execute the action.
    def __call__(self):
	raise NotImplementedError, '%s.__call__()' % (self.__class__.__name__,)
    pass

## \defgroup action_form_G Action Form
# \ingroup app_action_G
# \brief Action_form initialize form variables provided by user client.
#@{

## Setup form variables.
#
# It sets self.form to be a dictionary for an action.  The dictinary
# is a respository of variables from user clients.  It also sers
# self.env to deliver environment variables from HTTP daemons.
class action_form(object):
    def __init__(self, *args, **kws):
	super(action_form, self).__init__(*args, **kws)
	pass
    
    #form = mkundef('form')
    pass


## Action_form for CGI environment.
#
# It reads variables from PATH_INFO and CGI form variables.
# By definition of http://hoohoo.ncsa.uiuc.edu/cgi/env.html,
# PATH_INFO is
# \verbatim
#       The extra path information, as given by the client.
#       In other words, scripts can be accessed by their virtual
#       pathname, followed by extra information at the end of
#       this path.
# \endverbatim
class CGI_form(action_form):
    def __init__(self, *args, **kws):
	super(CGI_form, self).__init__(*args, **kws)
	pass
    
    def __full_with_CGI_form(self, res, form):
	for var in self._ival:
	    try:
                res[var] = self.to_utf8(form.getvalue(var))
                pass
            except:
		pass
	    pass
        # Upload files
	for var in self._fval:
	    try:
                res[var] = form[var]
                pass
            except:
		pass
	    pass
	pass
    
    def __full_with_path_info(self, res):
	encoding = GINGIN_ENCODING
	try:
	    if self.env['HTTP_USER_AGENT'].find(' MSIE ') >= 0:
		encoding = 'utf8'
	except:
	    pass
	try:
	    pinfo = split(self.env['PATH_INFO'], '/')[2:]
	    i = 0
	    while i < len(pinfo) and i < len(self._ival):
		var = self._ival[i]
		res[var] = self.to_utf8(pinfo[i], encoding)
		i = i + 1
	except KeyError:
	    pass
	pass

    ## Setup form/env variables from variables of CGI form and PATH_INFO.
    def set_form(self, form, env):
        self.env = env
	self.form = {}
	self.__full_with_CGI_form(self.form, form)
	self.__full_with_path_info(self.form)
	pass
    pass


## A mock of action_form.
#
# It is used for (unit) testing.
class test_form(action_form):
    def __init__(self, *args, **kws):
	super(test_form, self).__init__(*args, **kws)
	pass
    
    def set_form(self, form, env):
	self.form = form
        self.env = env
	pass
    pass

##@}

## \defgroup new_octr_G Output Control
# \ingroup app_action_G
# \brief Control and format output of actions.
#
# \ref new_octr control and format output of actions (\ref new_action).
# \ref action_octr is responsive to setup a new_octr for a new_action.
#@{

## Control ouptput of actions.
class new_octr(object):
    def __init__(self, *args, **kws):
        super(new_octr, self).__init__(*args, **kws)
        self.media_type = 'text/html'
        self.charset = GINGIN_ENCODING
        pass

    ## Setup media type (Content-Type) of output page.
    def set_media_type(self, mtype):
        self.media_type = mtype
        pass

    ## Setup charset of output page.
    def set_charset(self, chset):
        self.charset = chset
        pass
    
    #ofo = mkundef('ofo')
    pass

## Initialize self.octr as a new_octr.
class action_octr(object):
    def __init__(self, *args, **kws):
	super(action_octr, self).__init__(*args, **kws)
	pass
    
    #octr = mkundef('octr')
    pass


## Action_octr for CGI environment.
class CGI_octr(action_octr):
    def __init__(self, *args, **kws):
	super(CGI_octr, self).__init__(*args, **kws)
	pass
    
    def set_octr(self, octr):
	self.octr = octr
	pass
    pass

## A mock of new_octr.
#
# It is used for (unit) testing.
class test_octr(action_octr):
    def __init__(self, *args, **kws):
	import sys
	super(test_octr, self).__init__(*args, **kws)
	self.octr = new_octr()
	self.octr.ofo = sys.stdout
	pass
    octr = 1
    pass

## @}

# ========================================

## \defgroup actions_G GinGin's actions.
# \ingroup app_action_G
# @{

class default_act(new_action):
    def __init__(self):
        super(default_act, self).__init__('default_act',  ['func'])
        pass
    
    def __call__(self):
        form = self.form
        try:
            func = form['func']
        except:
            try:
                func = split(self.env['PATH_INFO'], '/')[1]
            except:
                func = ''
                pass
            pass
        return represent.error_page('no such function: %s' % (func),
                                    self.octr.ofo)
    pass

## Show the document with specified ID.
class show_id_doc(new_action):
    def __init__(self):
	super(show_id_doc, self).__init__('show_id_doc',  ['doc_id'])
	pass
	
    def __call__(self):
	from templates import doc
	from xml_template import escape_url

	doc_id = int(self.form['doc_id'])

        self.auth(doc_id)
	
	kws, doc_id, title, doc_body, pdate, uid, published = \
            GinGin_db.get_id_doc(doc_id)
	content = {}
	creator = GINGIN_USER.get_user_from_id(self, uid)
	all_kws = GinGin_db.get_all_kws()
	doc_body = GinGin_db.replace_kws(doc_body, all_kws)
	
	comments = GinGin_db.get_id_doc_comments(doc_id)
	comments = [{'msg': x[4],
                     'website': escape_url(x[3]),
                     'pdate': x[5],
                     'name': x[1]}
                    for x in comments]
	
	content['keywords'] = [{'keyword': kw} for kw in kws]
	content['doc_id'] = doc_id
	content['title'] = title
	content['text'] = doc_body
	content['pdate'] = pdate
	content['uid'] = uid
	content['creator'] = creator
	content['comment'] = comments
	
	doc.str = tools.hack_str
	
	return content, doc.doc(self.octr.ofo)
    pass


## Show the source of the document of specified ID.
class show_id_doc_src(new_action):
    def __init__(self):
	super(show_id_doc_src, self).__init__('show_id_doc_src',  ['doc_id'])
	
    def __call__(self):
	doc_id = int(self.form['doc_id'])

        self.auth(doc_id)

	kws, doc_id, title, doc_body, pdate, uid, published = \
            GinGin_db.get_id_doc(doc_id)
	creator = GINGIN_USER.get_user_from_id(self, uid)
	represent.show_doc_src(kws, doc_id, title, doc_body, pdate, creator)
	pass
    pass

	
## Show editor form for the document with specified ID.
class edit_id_doc(new_action):
    def __init__(self):
	super(edit_id_doc, self).__init__('edit_id_doc', ['doc_id'])
	pass
	
    def __call__(self):
	from templates import edit
	doc_id = int(self.form['doc_id'])
        self.auth(doc_id)
	
	kws, doc_id, title, doc_body, pdate, uid, published = \
            GinGin_db.get_id_doc(doc_id)
	
	content = {}
	content['keywords'] = [{'keyword': kw} for kw in kws]
	content['doc_id'] = doc_id
	content['title'] = title
	content['body'] = doc_body
        content['published'] = published and 'true' or 'false'
	
	edit.str = tools.hack_str
	
	return content, edit.edit(self.octr.ofo)
    pass


## Show unpublished docs.
class show_all_unpublished(new_action):
    def __init__(self):
        super(show_all_unpublished, self).__init__('show_all_unpublished', [])
        pass

    def __call__(self):
        from templates import unpublished

        user = self.auth()

        docs = GinGin_db.get_unpublished_docs()
        docs = [{'doc_id': doc[0], 'title': doc[1],
                 'pdate': doc[2], 'creator': doc[3]}
                for doc in docs]
        content = {'title': 'List of unpublished documents', 'docs': docs}
        return content, unpublished.unpublished(self.octr.ofo)
    pass


## Show all keywords of a GinGin system.
class show_all_kws(new_action):
    def __init__(self):
	super(show_all_kws, self).__init__('show_all_kws', [])
	pass
    
    def __call__(self):
	from templates import all_kws
	
	kws = GinGin_db.get_all_kws()
	kws = [{'keyword': kw} for kw in kws]
	content = {'title': 'All Keywords', 'keywords': kws, 'keywords_num': len(kws)}
	
	all_kws.str = tools.hack_str
	
	return content, all_kws.all_kws(self.octr.ofo)
    pass


## Update content of the document specified ID.
class update(new_action):
    def __init__(self):
	super(update, self).__init__('update',
                                         ['doc_id', 'title', 'keywords',
                                          'doc_body', 'update_pdate',
                                          'published'])
        pass
    
    def __call__(self):
        from tools import get_server_url

        form = self.form
	doc_id = int(form['doc_id'])
	user = self.auth(doc_id)
	
	try:
	    title = form['title']
	except:
	    return represent.error_page('TITLE is need!', self.octr.ofo)
	try:
	    kws = get_keywords(form['keywords'])
	except:
	    return represent.error_page('At least one keyword!',
                                        self.octr.ofo)
	try:
	    doc_body = form['doc_body']
	except:
	    doc_body = ''
	    pass
	
	try:
	    update_pdate = form['update_pdate']
	except:
	    update_pdate = None
	    pass
	if update_pdate == 'yes':
	    update_pdate = True
	    pass

        try:
            published = form['published']
        except:
            published = None
            pass
        if published == 'yes':
            published = True
            pass
	
	if len(doc_body) > MAX_DOC_SZ:
	    return represent.error_page('too long', self.octr.ofo)
        uid = GINGIN_USER.get_id_from_user(self, user)
        doc_id = GinGin_db.update_doc(doc_id, title, kws, doc_body,
                                      uid, update_pdate, published)
        base, spath = get_server_url(self.octr.env)
        represent.show_update_ok(doc_id, title, spath)
        return None

## Show documents and URLs of a keyword.
class show_kw_docs(new_action):
    def __init__(self):
	super(show_kw_docs, self).__init__('show_kw_docs', ['keyword'])
	pass
    
    def __call__(self):
	from templates import keyword
	from xml_template import escape_url
	
	kw = self.form['keyword'].decode('utf-8')
	docs = GinGin_db.get_kw_docs(kw)
	urls = GinGin_db.get_kw_urls(kw)
	if len(docs) > 1 or len(urls) > 0:
	    docs =[{'doc_id': d[0], 'title': d[1], 'pdate': d[2], 'creator': d[3]} for d in docs]
	    urls = [{'url_id': u[0], 'title': u[1], 'url': escape_url(u[2]), 'abstract': u[3], 'pdate': u[4], 'creator': u[5]} for u in urls]
	    content = {'name': kw, 'docs': docs, 'urls': urls, 'title': kw}
	    keyword.str = tools.hack_str
	    return content, keyword.keyword(self.octr.ofo)
	elif len(docs) == 1:
	    # why not redirect ?
	    base, spath = tools.get_server_url(self.env)
	    tgt = spath + '/show_id_doc/%d'
	    tools.redirect(self.octr.ofo, tgt % (docs[0][0],))
	else:
	    return represent.error_page('%s is not a keyword' % (kw),
                                        self.octr.ofo)
	pass
    pass

## Show a form for a new document.
class new_doc(new_action):
    def __init__(self):
	super(new_doc, self).__init__('new_doc', [])
	pass
	
    def __call__(self):
	from templates import edit
	content = {'keywords': [], 'doc_id': -1, 'title': '', 'body': ''}
	
	edit.str = tools.hack_str
	
	return content, edit.edit(self.octr.ofo)

## Upload an attachment.
class add_afile(new_action):
    def __init__(self):
        super(add_afile, self).__init__('add_afile',
                                        ['doc_id', 'afkey'],
                                        ['afile'])
        pass
	
    def __call__(self):
        form = self.form
	doc_id = int(form['doc_id'])
	self.auth(doc_id)
	
	afkey = form['afkey']
	afobj = form['afile'].file
	mtype = form['afile'].type
	GinGin_db.add_afile_to_doc(doc_id, afkey, afobj, mtype)
	represent.go_back(self.env)
        pass

## Delete an attachment.
class del_afile(new_action):
    def __init__(self):
	super(del_afile, self).__init__('del_afile', ['doc_id', 'afkey'])
        pass
	
    def __call__(self):
        form = self.form
	doc_id = int(form['doc_id'])
	self.auth(doc_id)
	
	afkey = form['afkey']
	GinGin_db.remove_afile_by_afkey(doc_id, afkey)
	represent.go_back(self.env)
        pass
	
## Get content of an attachement.
class get_afile(new_action):
    def __init__(self):
	super(get_afile, self).__init__('get_afile', ['doc_id', 'afkey'])
	
    def __call__(self):
        form = self.form
	doc_id = int(form['doc_id'])
        self.auth(doc_id)
	
	afkey = form['afkey']
	afname, mtype = \
            GinGin_db.get_afname_mtype_by_afkey(doc_id, afkey)
	if afname != None:
	    represent.send_file(afname, afkey, mtype)
	else:
	    represent.not_found(afkey)
            pass
        pass
    pass

## Show attachments of the document with specified ID.
class show_afiles(new_action):
    def __init__(self):
	super(show_afiles, self).__init__('show_afiles', ['doc_id'])
        pass
	
    def __call__(self):
        from templates import attaches
        
        form = self.form
	doc_id = int(form['doc_id'])
        self.auth(doc_id)

	afkeys = GinGin_db.get_afkeys_doc(doc_id)
        content = {'doc_id': doc_id,
                   'title': 'Attachments of doc #%d' % (doc_id)}
        _attaches = [{'afkey': afkey} for afkey in afkeys]
        content['attaches'] = _attaches
        content['num_attaches'] = len(_attaches)

        attaches.str = tools.hack_str
        return content, attaches.attaches(self.octr.ofo)
    pass

## Show URLs with specified keyword.
class show_kw_urls(new_action):
    def __init__(self):
	super(show_kw_urls, self).__init__('show_kw_urls', ['keyword'])
	pass
	
    def __call__(self):
	from templates import kw_urls
	form = self.form

	keyword = form['keyword'].decode('utf8')
	urls = GinGin_db.get_kw_urls(keyword)
	content = represent.show_kw_urls(keyword, urls)
	content['title'] = keyword
	
	kw_urls.str = tools.hack_str
	
	return content, kw_urls.kw_urls(self.octr.ofo)

## Unassociate URLs with specified keyword.
class del_kw_urls(new_action):
    def __init__(self):
	super(del_kw_urls, self).__init__('del_kw_urls', ['keyword', 'url_id'])
	
    def __call__(self):
	import types
	
	self.auth()
	form = self.form
	
        keyword = form['keyword']
        if form.has_key('url_id'):
            url_ids = form['url_id']
            if isinstance(url_ids, types.StringTypes):
                url_ids = [url_ids]
                pass
            url_ids = map(lambda x: int(x), url_ids)
            GinGin_db.del_kw_urls(keyword, url_ids)
        else:
            url_ids = []
            pass
	represent.show_del_kw_urls_ok(keyword, url_ids)

## Show document links for spider.
class show_to_robot(new_action):
    def __init__(self):
	super(show_to_robot, self).__init__('show_to_robot', [])
	
    def __call__(self):
	docs = GinGin_db.get_last_doc_ids(GINGIN_TO_ROBOT_N)
	represent.show_to_robot(docs, self.env)
	pass
    pass


## Return RSS feed of the GinGin system.
class rssfeed(new_action):
    def __init__(self):
	super(rssfeed, self).__init__('rssfeed', [])
	pass
    
    def __call__(self):
	from templates import rssfeed
	
	docs = GinGin_db.get_last_abstracts(GINGIN_TO_RSSFEED_N)
	docs = map(lambda x: (x[0], x[1], gingin_date_to_rss_date(x[2]), x[3], x[4]), docs)
	self.octr.set_media_type('application/xml')
	content = represent.show_rssfeed(docs)
	content['title'] = GINGIN_SITE
	
	rssfeed.str = tools.hack_str
	
	return content, rssfeed.rssfeed(self.octr.ofo), None
    pass

## Update/add an URL.
class update_url(new_action):
    def __init__(self):
	super(update_url, self).__init__('update_url', ['keywords', 'url_id', 'title', 'url', 'abstract'])
	pass
	
    def __call__(self):
	from templates import edit_url

	user = self.auth()
        
	try:
	    abstract = self.form['abstract']
	except KeyError:
	    abstract = ''
	try:
	    url_id = int(self.form['url_id'])
	    title = self.form['title']
	    url = self.form['url']
	    kws = self.form['keywords']
	    kws = get_keywords(kws)
	    if len(kws) == 0:
		return represent.error_page(
                    'you should specify at leat one keyword.',
                    self.octr.ofo)
            pass
        except KeyError:
	    return represent.error_page('paramter error', self.octr.ofo)
	uid = GINGIN_USER.get_id_from_user(self, user)
	url_id = GinGin_db.update_url(url_id, title, url, abstract, uid, kws)
	base, spath = tools.get_server_url(self.env)
	tools.redirect(self.octr.ofo, '%s/show_kw_urls/%s' % (spath, str(kws[0].decode('utf-8'))))
	pass
    pass


## Show a form for adding a new URL.
class edit_new_url(new_action):
    def __init__(self):
	super(edit_new_url, self).__init__('edit_new_url', [])
	pass
	
    def __call__(self):
	from templates import edit_url
	
	content = {'title': 'Edit a URL', 'url_id': -1, 'url_title': '', 'url': '', 'abstract': '', 'keywords': []}
	
	edit_url.str = tools.hack_str
	
	return content, edit_url.edit_url(self.octr.ofo)
    pass


## Show a form for editing an exisited URL.
class edit_url(new_action):
    def __init__(self):
	super(edit_url, self).__init__('edit_url', ['url_id'])
	pass
    
    def __call__(self):
	from templates import edit_url
	
	url_id = int(self.form['url_id'])
	url, kws = GinGin_db.get_url(url_id)
	
	content = {'title': 'Edit a URL',
                   'url_id': url_id,
                   'url_title': url[1],
                   'url': url[2],
                   'abstract': url[3]}
	content['keywords'] = [{'keyword': kw} for kw in kws]
	
	edit_url.str = tools.hack_str
	
	return content, edit_url.edit_url(self.octr.ofo)
    pass

## Show a form to create a new comment for the document with specified ID.
class edit_comment(new_action):
    def __init__(self):
	super(edit_comment, self).__init__('edit_comment', ['doc_id'])
	pass
    
    def __call__(self):
	from templates import comment
	
	doc_id = int(self.form['doc_id'])
	attack = GinGin_db.get_id_doc_attack(doc_id)
	content = {'title': 'Edit Comment', 'doc_id': doc_id, 'attack_plain': attack[1], 'attack_cipher': attack[2]}
	
	comment.str = tools.hack_str
	
	return content, comment.comment(self.octr.ofo)
    pass

## Add a comment to the document with specified ID.
class add_comment(new_action):
    def __init__(self):
	super(add_comment, self).__init__('add_comment', ['doc_id', 'key', 'name', 'email', 'website', 'msg'])
	pass
    
    def __call__(self):
        from tools import get_server_url

	form = self.form
	
	doc_id = int(form['doc_id'])
	key = form['key']
	name = form['name']
	email = form['email']
	if form.has_key('website'):
	    website = form['website']
	else:
	    website = None
	    pass
	msg = form['msg']
	GinGin_db.add_id_doc_comment(doc_id, name, email, website, msg, key)
	
        base, spath = get_server_url(self.octr.env)
        represent.show_update_ok(doc_id, '', spath)
	pass
    pass

## Show lastest comments of the GinGin system.
class last_comments(new_action):
    def __init__(self):
	super(last_comments, self).__init__('last_comments', [])
	pass
    
    def __call__(self):
	from templates import last_comments
	comments = GinGin_db.get_last_comments(GINGIN_LAST_COMMENTS_N)
	cmts = [{'cmt_id': c[0], 'doc_id': c[1], 'name': c[2], 'website': c[4], 'msg': c[5], 'pdate': c[6]} for c in comments]
	content = {'title': 'Last Comments', 'comments': cmts}
	
	last_comments.str = tools.hack_str
	
	return content, last_comments.last_comments(self.octr.ofo)

## Show trackback of a specified document.
class trackback(new_action):
    def __init__(self):
	super(trackback, self).__init__('trackback', ['doc_id', '__mod'])
        pass

    def __call__(self):
        form = self.form
	doc_id = int(form['doc_id'])
	
        self.auth(doc_id)

	if form.has_key('__mod'):
	    __mod = form['__mod']
	    if __mod in ('rss', 'view'):
		kws, doc_id, title, doc_body, pdate, uid, published = \
                    GinGin_db.get_id_doc(doc_id)
		desc = doc_body
		if len(desc) > GINGIN_TB_BODY_MAX:
		    desc = desc[:GINGIN_TB_BODY_MAX] + '...'
		link = get_url_of_doc(doc_id, self.env)
		pings = GinGin_db.get_trackback_pings(doc_id)
		if __mod == 'rss':
                    from templates import tb_rss
                    content = {'title': title,
                               'link': link,
                               'description': desc,
                               'language': GINGIN_LANG}
                    pings_ent = [{'title': ping[0],
                                  'description': ping[2],
                                  'link': ping[3]}
                                 for ping in pings]
                    content['items'] = pings_ent
                    tb_rss.str = tools.hack_str
                    self.octr.set_media_type('text/xml')
                    return content, tb_rss.tb_rss(self.octr.ofo), None
		else:
                    from templates import tb_view
                    tb_view.str = tools.hack_str
                    content = {'title': title,
                               'doc_id': doc_id,
                               'desc': desc,
                               'link': link}
                    pings_ent = [{'title': ping[1], 'url': ping[3]}
                                 for ping in pings]
                    content['pings'] = pings_ent
                    content['num_pings'] = len(pings_ent)
                    return content, tb_view.tb_view(self.octr.ofo), None
	    else:
		return represent.error_page('invalid mode: %s' % (__mod),
                                            self.octr.ofo)
	else:
	    try:
		if form.has_key('title'):
		    title = form['title']
		else:
		    title = ''
		    pass
		if len(title) > 128:
		    title = title[:128] + '...'
		    pass
		
		if form.has_key('excerpt'):
		    excerpt = form['excerpt']
		else:
		    excerpt = ''
		    pass
		if len(excerpt) > GINGIN_TB_BODY_MAX:
		    excerpt = excerpt[:GINGIN_TB_BODY_MAX] + '...'
		    pass
		
		url = form['url']
		if len(url) > 128:
		    url = url[:128]
		    pass
		
		if form.has_key('blog_name'):
		    blog_name = form['blog_name']
		else:
		    blog_name = ''
		    pass
		if len(url) > 128:
		    blog_name = blog[:128]
		    pass
		pass
	    except KeyError:
                emsg = 'invalid arguments'
            else:
                rhost = self.env['REMOTE_ADDR'] + ':' + self.env['REMOTE_PORT']
                if exist_doc_id(doc_id):
                    GinGin_db.trackback_ping(doc_id, title, excerpt, url, blog_name, rhost)
                    emsg = None
                else:
                    emsg = 'doc %d is not found' % (doc_id)
                    pass
                pass
            from templates import tb_ping_err
            tb_ping_err.str = tools.hack_str
            if emsg:
                msg = {'data': emsg}
                ecode = 1
            else:
                msg = []
                ecode = 0
                pass
            content = {'title': '', 'msg': msg, 'ecode': ecode}
            self.octr.set_media_type('text/xml')
            self.octr.set_charset('iso-8859-1')
            return content, tb_ping_err.tb_ping_err(self.octr.ofo), None
        pass
    pass

## @}

def full_side_bar_info(out):
    docs = GinGin_db.get_last_docs(GINGIN_MOST_RECENT_N)
    hot_kws = GinGin_db.get_hot_keywords(GINGIN_MOST_HOT_KWS)
    
    hks = map(lambda x: {'name': x[0], 'num': int(x[1])}, hot_kws)
    lds = map(lambda x: {'id': x[0], 'title': x[1]}, docs)
    out['hot_keys'] = {'key': hks}
    out['last_docs'] = {'doc': lds}
    return out


def _get_func_name(form, env):
    try:
        func = form['func'].value
    except KeyError:
        try:
            pinfo = env['PATH_INFO']
        except:
            return None
        func = split(pinfo, '/')[1]
        pass
    return func

def _fallback_homepage(form, env):
    func = 'show_id_doc'
    env = dict(env)
    env['PATH_INFO'] = '/show_id_doc/1'
    return func, form, env

def _show_error_page(form, env, octr):
    import sys
    import traceback
    tp, val, tb = sys.exc_info()
    while tb.tb_next:
        tb = tb.tb_next
        pass
    f = tb.tb_frame
    lno = traceback.tb_lineno(tb)
    emsg1 = '%s: %s\n\tin %s, L%d file \'%s\'\n' % (str(tp), str(val),
                                                    f.f_code.co_name,
                                                    lno,
                                                    f.f_code.co_filename)
    #emsg2 = 'locals: %s\nglobals: %s\n' % (repr(f.f_locals),
    #                                       repr(f.f_globals))
    return represent.error_page(emsg1, octr.ofo)

def GinGin_run_action(form, env, octr):
    import mez_xml.tools
    mez_xml.tools.str = tools.hack_str
    
    func = _get_func_name(form, env)
    if not func:
        func, form, env = _fallback_homepage(form, env)
        pass
    
    act_clazz = _all_actions_.setdefault(func, default_act)
    
    try:
        act = act_clazz()
        act.set_form(form, env)
        act.set_octr(octr)
        return act()
    except DENY_ACTION, e:
	return represent.show_deny(e.user, e.act_name, e.doc_id)
    except user.NO_LOGIN_ERR:
	GINGIN_USER.show_login(act)
    except user.REDIRECT, e:
        represent.redirect(e.url, e.msg)
    except:
        return _show_error_page(form, env, octr)
    pass

def _init_actions():
    global _all_actions_
    _all_actions_ = {}
    for name, obj in globals().items():
        if type(obj) == type and \
                obj != new_action and \
                issubclass(obj, new_action):
            mixin(obj, CGI_form)
            mixin(obj, CGI_octr)
            _all_actions_[name] = obj
            pass
        pass
    pass

_init_actions()

