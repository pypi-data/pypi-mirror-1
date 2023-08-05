import sys
from string import join

def trans_to_javascript(data):
    from types import StringType, ListType, TupleType, SliceType, NoneType
    from types import MethodType, FunctionType
    if type(data) == StringType:
	jstr = `data.decode('utf8')`[1:]
    elif type(data) == ListType or type(data) == TupleType or type(data) == SliceType:
	data = map(lambda x: trans_to_javascript(x), data)
	jstr = 'Array(' + join(data, ', ') + ')'
    elif type(data) == NoneType:
	jstr = 'null'
    elif isinstance(data, MethodType) or isinstance(data, FunctionType):
	jstr = data()
    else:
	jstr = `data`
    return jstr


def format_str_template(istr, data, jdata):
    ostr = istr
    for d in data.items():
	key = d[0]
	value = d[1]
	rep = '$' + key + '$'
	skip = len(rep)
	pos = ostr.find(rep)
	while pos >= 0:
	    attach = None
	    rvalue = value
	    try:
		#
		# Is it in form '$key${{{ ...... }}}'?
		#
		if ostr[pos:pos + len(rep)+3] == (rep + '{{{'):
		    epos = ostr.find('}}}', pos)
		    if epos > 0:
			apos = pos + len(rep) + 3
			attach = ostr[apos:epos]
			try:
			    rvalue = value(attach)
			except TypeError, e:
			    # not a callable
			    rvalue = 'error'
			    pass
			skip = epos + 3 - pos
	    except IndexError:
		pass
	    ostr = ostr[:pos] + rvalue + ostr[pos + skip:]
	    pos = ostr.find(rep, pos + skip)
    for d in jdata.items():
	key = d[0]
	value = d[1]
	rep = '$' + key + '$'
	pos = ostr.find(rep)
	while pos >= 0:
	    repstr = trans_to_javascript(value)
	    ostr = ostr[:pos] + repstr + ostr[pos + len(rep):]
	    pos = ostr.find(rep, pos + len(rep))
    return ostr


def format_template(fn, data, jdata):
    fo = open(fn, 'r')
    istr = fo.read()
    fo.close()
    
    sys.stdout.write(format_str_template(istr, data, jdata))
	
