#! env python

class NO_LOGIN_ERR:
    def __init__(self):
	pass


class anony_user:
    def __init__(self):
	pass
    
    def get_login_user(self):
	return 'guest'
    
    def get_id_from_user(self, name):
	return 'guest'
    
    def get_user_from_id(self, uid):
	return 'guest'
    
    def authorize(self, user, task, doc_id=-1):
	return 1
    
    def login(self, form):
	print 'Content-Type: text/html'
	print
	print 'Do not support login()'
    
    def show_login(self):
	print 'Content-Type: text/html'
	print
	print 'Do not support show_login()'


class HTTP_auth:
    def __init__(self):
	pass
    
    def get_login_user(self):
	import os
	user = None
	try:
	    user = os.environ['REMOTE_USER']
	except:
	    pass
	return user
    
    def get_id_from_user(self, name):
	return name
    
    def get_user_from_id(self, uid):
	return uid
    
    def authorize(self, user, task, doc_id=-1):
	import os
	method = os.environ['REQUEST_METHOD']
	if (task in ('update', 'add_afile', 'del_afile',
                     'update_url', 'del_kw_urls')) and \
           (user == None or method != 'POST'):
	    raise NO_LOGIN_ERR()
	return 1
    
    def login(self, form):
	print 'Content-Type: text/html'
	print
	print 'Do not support login()'
    
    def show_login(self):
	import os
	print 'Content-Type: text/plain'
	print 'Status: 401 Authentication is required.'
	print 'WWW-Authenticate: Basic realm="By Invitation Only"'
	print
	print 'Error if you can see this document!'
	print 'Please ask administractor to start HTTP Authentication'
	print 'for posting to GinGin_CGI.py.'

