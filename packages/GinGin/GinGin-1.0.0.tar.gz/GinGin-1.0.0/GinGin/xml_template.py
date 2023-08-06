from string import join
import re

def escape_cdata(data):
    reo_xml_spec = re.compile('[&<>]')
    parts = []
    last_pos = 0
    mo = reo_xml_spec.search(data, last_pos)
    while mo != None:
	pos = mo.start()
	c = data[pos]
	if c == '&':
	    c = '&amp;'
	elif c == '<':
	    c = '&lt;'
	else:
	    c = '&gt;'
	parts.append(data[last_pos:pos] + c)
	last_pos = pos + 1
	mo = reo_xml_spec.search(data, last_pos)
    parts.append(data[last_pos:])
    return join(parts, '')

def escape_url(url):
    if not url:
	return 'http://invalid/empty/url'
    if not (url.startswith('http:') or url.startswith('HTTP:')):
	url = 'http://invalid/' + url
	pass
    url = url.replace('<', '%3C')
    url = url.replace('>', '%3E')
    url = url.replace('\'', '%27')
    url = url.replace('"', '%22')
    url = url.replace('\\', '%5C')
    url = url.replace(' ', '%20')
    return url

def trans_to_xml(data, tag='', lvl=0):
    from types import StringTypes, ListType, TupleType, SliceType, NoneType
    from types import MethodType, FunctionType, DictType
    indent = '  ' * lvl
    if type(data) in (ListType, TupleType, SliceType):
	items = map(lambda x: trans_to_xml(x, tag, lvl), data);
	retr = join(items, '')
    elif type(data) in (MethodType, FunctionType):
	retr = trans_to_xml(data(), tag, lvl)
    elif isinstance(data, DictType):
	sub_retr = map(lambda x:trans_to_xml(x[1], x[0], lvl + 1), data.items())
	sub_retr = join(sub_retr, '')
	retr = u'%s<%s>\n%s%s</%s>\n' % (indent, tag, sub_retr, indent, tag)
    elif isinstance(data, StringTypes):
	retr = u'%s<%s>%s</%s>\n' % (indent, tag, data, tag)
    else:
	retr = u'%s<%s>%s</%s>\n' % (indent, tag, str(data), tag)
    return retr


if __name__ == "__main__":
    from types import DictType
    d = {'a': 123, 'b': 'kkk', 'c': (1, 2, 3)}
    print type(d), DictType
    print trans_to_xml(d, 'test')
