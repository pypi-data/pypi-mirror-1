# -*-: big5
from mez_xml.tools import nez_web

class gingin(nez_web):
    def __init__(self, ofo):
        super(gingin, self).__init__()
        self.ofo = ofo
        pass
    
    def _root(self, pdata, cdata):
        def temp(data):
            self.ofo.write('''<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta value="text/html; charset=big5" http-equiv="Content-Type"></meta>
<link href="''')
            odata = data.setdefault('gingin_url', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write('''/rssfeed" type="application/rss+xml" rel="alternate" title="''')
            odata = data.setdefault('site', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write(''' RSS Feed"></link>
<title>''')
            odata = data.setdefault('title', {})
            self.ofo.write(self._esc_text(odata))
            self.ofo.write('''</title>
<link href="''')
            odata = data.setdefault('base_url', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write('''/GinGin.css" type="text/css" rel="stylesheet"></link>
''')
            cdata = data.setdefault('headcontent', {})
            self.headcontent(data, cdata)
            self.ofo.write('''
<script src="''')
            odata = data.setdefault('base_url', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write('''/js/GinGin.js" type="text/javascript" language="javascript">
<![CDATA[
dummy = 1;
]]>
</script>
<script type="text/javascript" language="javascript">
<!--
var init_funcs = new Array();

function call_init() {
	var i;

	for(i in init_funcs) {
		init_funcs[i]();
	}
}
-->
</script>
</head>

<body onload="javascript: call_init()">
<table id="outer">
<tr>
<td>

<!-- LAST DOCUMENTS -->
<div id="hide_bar"><a href="''')
            odata = data.setdefault('gingin_url', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write('''/show_to_robot/">robot</a></div>
<div id="sidebar">
<div id="last_docs">
<div class="title">最新文章(''')
            odata = data.setdefault('last_docs_num', {})
            self.ofo.write(self._esc_text(odata))
            self.ofo.write(''')</div>
<ul>
''')
            cdata = data.setdefault('last_docs', {})
            self.last_docs(data, cdata)
            self.ofo.write('''
</ul>
<a href="''')
            odata = data.setdefault('gingin_url', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write('''">首頁</a><a href="''')
            odata = data.setdefault('gingin_url', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write('''/new_doc">新編</a><a href="''')
            odata = data.setdefault('gingin_url', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write('''/last_comments">最新留言</a><br></br>
<a href="''')
            odata = data.setdefault('gingin_url', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write('''/rssfeed">Entries RSS</a></div>

<!-- HOT KEYWORDS -->
<div id="hot_kws">
<div class="title">重要關鍵字(''')
            odata = data.setdefault('hot_kws_num', {})
            self.ofo.write(self._esc_text(odata))
            self.ofo.write(''')</div>
<ul>
''')
            cdata = data.setdefault('hot_kws', {})
            self.hot_kws(data, cdata)
            self.ofo.write('''
</ul>
<a href="''')
            odata = data.setdefault('gingin_url', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write('''/show_all_kws">所有關鍵字</a><br></br>
<a href="''')
            odata = data.setdefault('gingin_url', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write('''/edit_new_url">新增 URL</a>
</div>

''')
            cdata = data.setdefault('non_public', {})
            self.non_public(data, cdata)
            self.ofo.write('''

<div>
''')
            cdata = data.setdefault('personal_info', {})
            self.personal_info(data, cdata)
            self.ofo.write('''
</div>
</div>

</td><td>

''')
            cdata = data.setdefault('content', {})
            self.content(data, cdata)
            self.ofo.write('''

</td>
</tr>
</table>

</body>
</html>''')
            pass
        self._feed_subtree(temp, pdata, cdata)
        pass
    
    def headcontent(self, pdata, cdata):
        def temp(data):
            self.ofo.write('''<link ezid="headcontent"></link>''')
            pass
        self._feed_subtree(temp, pdata, cdata)
        pass
    
    def last_docs(self, pdata, cdata):
        def temp(data):
            self.ofo.write('''<li ezid="last_docs"><a href="''')
            odata = data.setdefault('gingin_url', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write('''/show_id_doc/''')
            odata = data.setdefault('id', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write('''">''')
            odata = data.setdefault('title', {})
            self.ofo.write(self._esc_text(odata))
            self.ofo.write('''</a></li>''')
            pass
        self._feed_subtree(temp, pdata, cdata)
        pass
    
    def hot_kws(self, pdata, cdata):
        def temp(data):
            self.ofo.write('''<li ezid="hot_kws"><a href="''')
            odata = data.setdefault('gingin_url', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write('''/show_kw_docs/''')
            odata = data.setdefault('name', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write('''">''')
            odata = data.setdefault('name', {})
            self.ofo.write(self._esc_text(odata))
            self.ofo.write(''' (''')
            odata = data.setdefault('num', {})
            self.ofo.write(self._esc_text(odata))
            self.ofo.write(''')</a></li>''')
            pass
        self._feed_subtree(temp, pdata, cdata)
        pass
    
    def non_public(self, pdata, cdata):
        def temp(data):
            self.ofo.write('''<div ezid="non_public" id="non_public">
<div class="title">非公開</div>
<ul>
<li><a href="''')
            odata = data.setdefault('gingin_url', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write('''/show_all_unpublished">未發佈</a></li>
</ul>
</div>''')
            pass
        self._feed_subtree(temp, pdata, cdata)
        pass
    
    def personal_info(self, pdata, cdata):
        def temp(data):
            self.ofo.write('''<div ezid="personal_info"></div>''')
            pass
        self._feed_subtree(temp, pdata, cdata)
        pass
    
    def content(self, pdata, cdata):
        def temp(data):
            self.ofo.write('''<div ezid="content" id="content">
</div>''')
            pass
        self._feed_subtree(temp, pdata, cdata)
        pass
    
    pass

