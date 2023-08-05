#!/usr/local/bin/python
import unittest
import GinGin_acts as acts
import config
from GinGin_acts import mixin
from GinGin_CGI import page_framework

class test_actions(unittest.TestCase):
    def setUp(self):
	pass
    
    def test_show_id_doc(self):
	mixin(acts.show_id_doc, acts.test_form)
	mixin(acts.show_id_doc, acts.test_octr)
	act_o = acts.show_id_doc()
	act_o.set_form({'doc_id': '1'})
	data, temp = act_o()
	
	from templates import doc, gingin
	def hack_str(s):
	    if isinstance(s, unicode):
		return s.encode(config.GINGIN_ENCODING)
	    return str(s)
	gingin.str = doc.str = hack_str
	
	pfwrk = page_framework()
	pfwrk.get_server_url = lambda: ('/', '/GinGin_CGI.py')
	pfwrk(data, temp, act_o.octr)
	pass
    pass

suite = unittest.TestLoader().loadTestsFromTestCase(test_actions)
unittest.TextTestRunner(verbosity=2).run(suite)
