#!/usr/local/bin/python
import sys
import represent
import GinGin_acts
import tools
from config import *


# DONE: Attach an output file and environment variables on output_ctr.
class output_ctr:
    def __init__(self, out, env):
	self.mix= True
	self.media_type = 'text/html'
        self.charset = GINGIN_ENCODING
	self.ofo = out
        self.env = env
	pass
    
    def set_last_modified(self, tm):
	self.last_modified = tm
	pass
    
    def clear_last_modified(self):
	del self.last_modified
	pass
    
    def stop_mix(self):
	self.mix = False
	
    def set_media_type(self, mtype):
	self.media_type = mtype
	pass

    def set_charset(self, chset):
        self.charset = chset
        pass
    pass


def send_http_header(octr):
    from time import asctime, gmtime
    try:
	print >> octr.ofo, 'Last-Modified: ' + octr.last_modified
    except AttributeError:
	pass
    print >> octr.ofo, 'Content-Type: ' + octr.media_type + '; charset=' + GINGIN_ENCODING
    print >> octr.ofo
    pass


class page_framework(object):
    get_server_url = tools.mk_not_imp('get_server_url')
    
    def __init__(self, skel_page):
	super(page_framework, self).__init__()
	self._skel_page = skel_page
	pass
    
    def get_last_docs(self):
	import GinGin_db
	docs = GinGin_db.get_last_docs(GINGIN_MOST_RECENT_N)
	r = [{'id': doc[0], 'title': doc[1]} for doc in docs]
	return r
    
    def get_hot_keywords(self):
	import GinGin_db
	from xml_template import escape_cdata
	hot_kws = GinGin_db.get_hot_keywords(GINGIN_MOST_HOT_KWS)
	r  = [{'name': kw[0], 'num': kw[1]} for kw in hot_kws]
	return r
    
    def __call__(self, data, temp, octr, env):
        from templates import gingin
        
	base, spath = self.get_server_url(env)
	
	if hasattr(gingin.gingin, 'content'):
	    del gingin.gingin.content
	    pass
	if self._skel_page:
	    page = self._skel_page(octr.ofo)
	    page.content = temp._root
	else:
	    page = temp
	    pass
	temp.safe = True
	page.safe = True
	
	pdata = {'content': data}
	pdata['site'] = GINGIN_SITE
	pdata['base_url'] = base
	pdata['gingin_url'] = spath
	pdata['title'] = data['title']
	pdata['last_docs'] = self.get_last_docs()
	pdata['last_docs_num'] = len(pdata['last_docs'])
	pdata['hot_kws'] = self.get_hot_keywords()
	pdata['hot_kws_num'] = len(pdata['hot_kws'])
        user = GINGIN_USER.get_login_user(octr)
        if user == None:
            pdata['non_public'] = ''
            pass
	page.gen_doc(pdata)
	pass
    pass

def GinGin(req):

    # actin_out is the output of request action.
    # If it is None, the action had generated output page for them-self,
    # or action_out comprises data, template, and, maybe, page skelelton
    # waiting for rendering.  Here, we render the data for it.
    form = req.getFieldStorage()
    try:
        octr = output_ctr(req.out, req.env)
        GinGin_acts.str = tools.hack_str
	action_out = GinGin_acts.GinGin_run_action(form, req.env, octr)
    except:
	import traceback
	tb_str = traceback.format_exc()
	tb_str = tb_str.replace('<', '&lt;')
	tb_str = tb_str.replace('>', '&gt;')
	data, temp, page_skel = represent.error_page('EXCEPTION:\n' + tb_str, octr.ofo)
        send_http_header(octr)
        temp.gen_doc(data)
        sys.exit(0)
	
    if action_out != None:       # There is data waiting for rendering
        # Render the data.
        from templates import gingin
        
        # page_skel is outest skeleton of output page.
        # data is data being showed by output page.
        # temp is the template used to render data.
        #
        # The result of rendering is ovened with page_skel to create
        # output page.
        if len(action_out) == 2:
            data, temp = action_out
            page_skel = gingin.gingin
            gingin.str = tools.hack_str
        elif len(action_out) == 3:  # actin_out is with page_skel
            data, temp, page_skel = action_out
            pass
        pfwrk = page_framework(page_skel)
        pfwrk.get_server_url = tools.get_server_url
        send_http_header(octr)
        octr.ofo.write("<?xml version=\"1.0\" encoding=\"%s\"?>\n" % (octr.charset,))
        if octr.media_type == 'text/html':
            octr.ofo.write('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\n')
            pass
        pfwrk(data, temp, octr, req.env)
        #sys.exit(0)
        pass
    pass

if __name__ == '__main__':
    import fcgi

    while fcgi.isFCGI():
        req = fcgi.Accept()
        GinGin(req)
        req.Finish()
        pass
    pass
