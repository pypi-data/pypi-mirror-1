# -*-: big5
from mez_xml.tools import nez_web

class doc(nez_web):
    def __init__(self, ofo):
        super(doc, self).__init__()
        self.ofo = ofo
        pass
    
    def _root(self, pdata, cdata):
        def temp(data):
            self.ofo.write('''<div id="content">
<div class="title">
''')
            odata = data.setdefault('title', {})
            self.ofo.write(self._esc_text(odata))
            self.ofo.write('''

<div class="creator">
by ''')
            odata = data.setdefault('creator', {})
            self.ofo.write(self._esc_text(odata))
            self.ofo.write('''
</div>

</div>
<div style="float: right" class="keyword">
<a href="javascript: init_mcol()">
2 Columns
</a>
</div>
<div class="keywords">
關鍵字:
<div class="keyword">
''')
            cdata = data.setdefault('keywords', {})
            self.keywords(data, cdata)
            self.ofo.write('''
</div>
</div>

<div class="rawtext" id="body">
<textarea id="rawbody">
''')
            odata = data.setdefault('text', {})
            self.ofo.write(self._esc_text(odata))
            self.ofo.write('''
</textarea>
</div>

<div class="utime">
最後更新時間:
''')
            odata = data.setdefault('pdate', {})
            self.ofo.write(self._esc_text(odata))
            self.ofo.write(''' |
<a href="''')
            odata = data.setdefault('base_url', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write('''GinGin_TB.py/trackback/''')
            odata = data.setdefault('doc_id', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write('''?__mod=view" onclick="open_trackback(this.href); return false;">
引用
</a>
</div>

<script src="''')
            odata = data.setdefault('base_url', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write('''/js/mcol.js" type="text/javascript" language="javascript">
dummy = 1;
</script>
<script src="''')
            odata = data.setdefault('base_url', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write('''/js/gindoc.js" type="text/javascript" language="javascript">
dummy = 1;
</script>
<script src="''')
            odata = data.setdefault('base_url', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write('''/js/show_doc_body.js" type="text/javascript" language="javascript">
dummy = 1;
</script>
<script src="''')
            odata = data.setdefault('base_url', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write('''/js/init_mcol.js" type="text/javascript" language="javascript">
dummy = 1;
</script>
<script>
<!--
var gingin_url = "''')
            odata = data.setdefault('gingin_url', {})
            self.ofo.write(self._esc_comm(odata))
            self.ofo.write('''";
var doc_id = ''')
            odata = data.setdefault('doc_id', {})
            self.ofo.write(self._esc_comm(odata))
            self.ofo.write(''';
var rawbody = document.getElementById("rawbody");
var body = document.getElementById("body");
rawbody.value = rawbody.value.replace("&", "&amp;", "g");
rawbody.value = rawbody.value.replace("<", "&lt;", "g");
rawbody.value = rawbody.value.replace(">", "&gt;", "g");
-->
</script>

<div id="func_bar">
<input accesskey="E" type="button" onclick="edit()" value="編輯(E)"></input>
<input accesskey="N" type="button" onclick="new_doc()" value="新編(N)"></input>
<input accesskey="A" type="button" onclick="show_afiles()" value="附加(A)"></input>
<input accesskey="C" type="button" onclick="show_edit_comment()" value="留言(C)"></input>
<input type="button" onclick="all_kws()" value="所有關鍵字"></input>
查詢:<input onchange="query(this.value)" type="text" value="關鍵字"></input>
</div>

<div id="comments">
COMMENTS:
''')
            cdata = data.setdefault('comment', {})
            self.comment(data, cdata)
            self.ofo.write('''
</div>

<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:trackback="http://madskills.com/public/xml/rss/module/trackback/" xmlns:dc="http://purl.org/dc/elements/1.1/">
    <rdf:Description trackback:ping="''')
            odata = data.setdefault('gingin_url', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write('''/trackback/''')
            odata = data.setdefault('doc_id', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write('''" dc:title="''')
            odata = data.setdefault('site', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write(''': ''')
            odata = data.setdefault('title', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write('''" rdf:about="''')
            odata = data.setdefault('gingin_url', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write('''/show_id_doc/''')
            odata = data.setdefault('doc_id', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write('''" dc:identifier="''')
            odata = data.setdefault('gingin_url', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write('''/show_id_doc/''')
            odata = data.setdefault('doc_id', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write('''"></rdf:Description>
</rdf:RDF>

</div>''')
            pass
        self._feed_subtree(temp, pdata, cdata)
        pass
    
    def keywords(self, pdata, cdata):
        def temp(data):
            self.ofo.write('''<a ezid="keywords" href="''')
            odata = data.setdefault('gingin_url', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write('''/show_kw_docs/''')
            odata = data.setdefault('keyword', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write('''">
''')
            odata = data.setdefault('keyword', {})
            self.ofo.write(self._esc_text(odata))
            self.ofo.write('''
</a>''')
            pass
        self._feed_subtree(temp, pdata, cdata)
        pass
    
    def comment(self, pdata, cdata):
        def temp(data):
            self.ofo.write('''<div ezid="comment" class="comment">
<div class="pdate">on ''')
            odata = data.setdefault('pdate', {})
            self.ofo.write(self._esc_text(odata))
            self.ofo.write('''</div>
<span class="name"><a href="''')
            odata = data.setdefault('website', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write('''">''')
            odata = data.setdefault('name', {})
            self.ofo.write(self._esc_text(odata))
            self.ofo.write('''</a> said ..</span>
<div class="msg">
''')
            odata = data.setdefault('msg', {})
            self.ofo.write(self._esc_text(odata))
            self.ofo.write('''
</div>
</div>''')
            pass
        self._feed_subtree(temp, pdata, cdata)
        pass
    
    pass

