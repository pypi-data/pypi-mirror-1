# -*-: big5
from mez_xml.tools import nez_web

class edit_url(nez_web):
    def __init__(self, ofo):
        super(edit_url, self).__init__()
        self.ofo = ofo
        pass
    
    def _root(self, pdata, cdata):
        def temp(data):
            self.ofo.write('''<div id="content">

<div class="title">
新增/編輯 URL
</div>

<div class="text">
<form action="''')
            odata = data.setdefault('base_url', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write('''GinGin_CGI.py" method="post">
<input type="hidden" name="func" value="update_url"></input>
<input type="hidden" name="url_id" value="''')
            odata = data.setdefault('url_id', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write('''"></input>
<table>
<tr>
 <td>標題</td>
 <td><input size="40" type="text" name="title" value="''')
            odata = data.setdefault('url_title', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write('''" maxlength="80"></input></td>
</tr>

<tr>
 <td>URL</td><td>
 <input size="40" type="text" name="url" value="''')
            odata = data.setdefault('url', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write('''" maxlength="160"></input></td>
</tr>

<tr>
 <td>摘要</td>
 <td><textarea rows="5" name="abstract" cols="40">''')
            odata = data.setdefault('abstract', {})
            self.ofo.write(self._esc_text(odata))
            self.ofo.write('''</textarea></td>
</tr>

<tr>
 <td>關鍵字</td>
 <td>
<input size="40" maxlength="200" type="text" id="keywords" name="keywords"></input>
<div id="kw_store">
''')
            cdata = data.setdefault('keywords', {})
            self.keywords(data, cdata)
            self.ofo.write('''
</div>
<script type="text/javascript" language="javascript">
<!--
function show_keyword() {
	var kws_o = document.getElementById("keywords");
	var kw_store = document.getElementById("kw_store");
	var span_o;
	var kws = [];
	var i;

	for(i = 0; i < kw_store.childNodes.length; i++) {
		if(kw_store.childNodes[i].tagName == "span" || kw_store.childNodes[i].tagName == "SPAN") {
			span_o = kw_store.childNodes[i];
			kws.push(span_o.childNodes[0].data);
		}
	}
	kws_o.setAttribute("value", kws.join("; "));
	kw_store.parentNode.removeChild(kw_store);
}
init_funcs.push(show_keyword);
-->
</script>
 </td>
</tr>
</table>

<input type="submit" value="確定"></input>
</form>
* 以此 script 新增 URL:
<a href="javascript: void(window.open("''')
            odata = data.setdefault('base_url', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write('''add_url.html?title=" + escape(document.title) + "&url=" + escape(document.URL), "gingin_url", "toolbar=no,menubar=no,width=500,height=300"))">
Bookmark</a>
</div>

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

