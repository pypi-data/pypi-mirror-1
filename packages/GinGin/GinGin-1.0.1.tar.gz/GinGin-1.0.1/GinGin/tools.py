from config import GINGIN_ENCODING

def list_pair_to_pairs_list(l1, l2):
    assert(len(l1) == len(l2))
    return [(l1[i], l2[i]) for i in range(len(l1))]

def get_server_url(env):
    spath = 'http://' + env['SERVER_NAME']
    if env['SERVER_PORT'] != '80':
	spath = spath + ':' + env['SERVER_PORT']
    spath = spath + env['SCRIPT_NAME']
    last = spath.rfind('/')
    base = spath[:last+1]
    return base, spath

def mk_not_imp(name):
    def _not_imp(self, *args, **kws):
	raise NotImplementedError, '%s.%s()' % (self.__class__.__name__, name)
    return _not_imp

def hack_str(s):
    if isinstance(s, unicode):
	return s.encode(GINGIN_ENCODING)
    return str(s)

def redirect(ofo, url):
    ofo.write('Location: %s\n' % (url,))
    ofo.write('Content-Type: text/html; charset=' + GINGIN_ENCODING + '\n')
    ofo.write('\n\n<html><body><a href="%s">%s</a></body></html>\n' % (url, url))
    pass
