# -*-: big5
from mez_xml.tools import nez_web

class edit(nez_web):
    def __init__(self, ofo):
        super(edit, self).__init__()
        self.ofo = ofo
        pass
    
    def _root(self, pdata, cdata):
        def temp(data):
            self.ofo.write('''<div class="content">
<div class="title">編輯</div>
<form action="''')
            odata = data.setdefault('gingin_url', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write('''" method="post">
<input type="hidden" name="func" value="update"></input>
<input type="hidden" id="doc_id" value="''')
            odata = data.setdefault('doc_id', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write('''" name="doc_id"></input>
<table>
<tr><td>

<table>
<tr>
<td>標題(I)</td>
<td>
<input name="title" accesskey="I" value="''')
            odata = data.setdefault('title', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write('''" maxlength="80" type="text" id="title" size="60"></input>
</td>
</tr>
<tr>
<td>關鍵字(K)</td>
<td>
<input name="keywords" accesskey="K" maxlength="200" type="text" id="keywords" size="40"></input>
<input checked="yes" type="checkbox" name="update_pdate"></input>更新修改日期
<input checked="''')
            odata = data.setdefault('published', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write('''" type="checkbox" id="published" name="published"></input>發佈
<div id="kw_store">
''')
            cdata = data.setdefault('keywords', {})
            self.keywords(data, cdata)
            self.ofo.write('''
</div>
<script>
<!--
var kws_o = document.getElementById("keywords");
var kw_store = document.getElementById("kw_store");
var i, kws;
kws = "";
for(i = 0; i < kw_store.childNodes.length; i++) {
	child = kw_store.childNodes[i];
	if(child.tagName == "span" || child.tagName == "SPAN") {
		kws = kws + child.childNodes[0].data + ";";
	}
}
kws_o.setAttribute("value", kws);
kw_store.parentNode.removeChild(kw_store);
var published = document.getElementById("published");
if(published.getAttribute("checked") == "true")
	published.checked = true;
else
	published.checked = false;
-->
</script>
</td>
</tr>
</table>

</td></tr>
<tr><td>
(T)<br></br>   
<textarea accesskey="T" rows="20" cols="70" id="doc_body" name="doc_body">''')
            odata = data.setdefault('body', {})
            self.ofo.write(self._esc_text(odata))
            self.ofo.write('''</textarea>
</td></tr>
</table>
<input accesskey="S" type="submit" value="更新(S)"></input>
</form>
		
</div>''')
            pass
        self._feed_subtree(temp, pdata, cdata)
        pass
    
    def keywords(self, pdata, cdata):
        def temp(data):
            self.ofo.write('''<span ezid="keywords">''')
            odata = data.setdefault('keyword', {})
            self.ofo.write(self._esc_text(odata))
            self.ofo.write('''</span>''')
            pass
        self._feed_subtree(temp, pdata, cdata)
        pass
    
    pass

