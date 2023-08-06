#! env python

class NO_LOGIN_ERR:
    def __init__(self):
	pass


class REDIRECT:
    def __init__(self, url, msg):
        self.url = url
        self.msg = msg
	pass


# DONE: Use 'env' from octr instead of 'os.environ'.
class anony_user:
    def __init__(self):
	pass
    
    def get_login_user(self, octr):
	return 'guest'
    
    def get_id_from_user(self, act, name):
	return 'guest'
    
    def get_user_from_id(self, act, uid):
	return 'guest'
    
    def authorize(self, act, user, task, doc_id=-1):
	return 1
    
    def login(self, act, form):
	print 'Content-Type: text/html'
	print
	print 'Do not support login()'
    
    def show_login(self, act):
	print 'Content-Type: text/html'
	print
	print 'Do not support show_login()'


class HTTP_auth:
    def __init__(self):
	pass
    
    def get_login_user(self, octr):
	import os
	user = None
	try:
	    user = octr.env['REMOTE_USER']
	except:
	    pass
	return user
    
    def get_id_from_user(self, act, name):
	return name
    
    def get_user_from_id(self, act, uid):
	return uid
    
    def authorize(self, act, user, task, doc_id=-1):
	import os, GinGin_db

        # When a action need to be authorized before using it,
        # it is redirected to GinGin_CGI_s.py for authory.
        # GinGin_CGI_s.py is authorized with HTTP authorization
        # against a password file specified in .htaccess
        def auth_first():
            import tools
            base, spath = tools.get_server_url(act.octr.env)
            url = base + 'GinGin_CGI_s.py'
            if act.octr.env.has_key('PATH_INFO'):
                url = url + act.octr.env['PATH_INFO']
                pass
            if act.octr.env.has_key('QUERY_STRING') and \
                    act.octr.env['QUERY_STRING']:
                url = url + '?' + act.octr.env['QUERY_STRING']
                pass
	    raise REDIRECT(url, 'Authory your-self, first.')

	method = act.octr.env['REQUEST_METHOD']
        # TODO: improve performance of matching tasks.
	if (task in ('update', 'add_afile', 'del_afile',
                     'update_url', 'del_kw_urls')) and \
           (user == None or method != 'POST'):
            auth_first()
            pass
        if (task == 'show_all_unpublished') and \
           (user == None or method != 'GET'):
            auth_first()
            pass
        if (task in ('show_afiles', 'get_afile', 'show_id_doc',
                     'show_id_doc_src', 'edit_id_doc', 'trackback')) and \
           (method != 'GET' or
            ((user == None) and (not GinGin_db.is_doc_published(doc_id)))):
            auth_first()
            pass
	return 1
    
    def login(self, act, form):
	print 'Content-Type: text/html'
	print
	print 'Do not support login()'
    
    def show_login(self, act):
	import os
	print 'Content-Type: text/plain'
	print 'Status: 401 Authentication is required.'
	print 'WWW-Authenticate: Basic realm="By Invitation Only"'
	print
	print 'Error if you can see this document!'
	print 'Please ask administractor to start HTTP Authentication'
	print 'for posting to GinGin_CGI.py.'

