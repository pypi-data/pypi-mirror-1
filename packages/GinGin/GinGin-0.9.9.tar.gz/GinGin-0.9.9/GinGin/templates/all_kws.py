# -*-: big5
from mez_xml.tools import nez_web

class all_kws(nez_web):
    def __init__(self, ofo):
        super(all_kws, self).__init__()
        self.ofo = ofo
        pass
    
    def _root(self, pdata, cdata):
        def temp(data):
            self.ofo.write('''<div id="content">
<div class="title">
共有 ''')
            odata = data.setdefault('keywords_num', {})
            self.ofo.write(self._esc_text(odata))
            self.ofo.write(''' 個關鍵字:
</div>

<div class="text">
<div id="keywords">
''')
            cdata = data.setdefault('keywords', {})
            self.keywords(data, cdata)
            self.ofo.write('''
</div>
<script type="text/javascript" language="javascript">
<!--
function create_table(data) {
	var tb = document.createElement("table");
	var tr, td;
	var i, j;

	for(i in data) {
		tr = document.createElement("tr");
		for(j in data[i]) {
			td = document.createElement("td");
			td.appendChild(data[i][j]);
			tr.appendChild(td);
		}
		tb.appendChild(tr);
	}
	return tb;
}

function show_keywords() {
	var kws_o = document.getElementById("keywords");
	var kw_o, kws_p_o;
	var kws = [];
	var tb = [], tb_c;
	var tb_o, a_o, txt_o;
	var i, j;

	for(i = 0; i < kws_o.childNodes.length; i++) {
		kw_o = kws_o.childNodes[i];
		if(kw_o.tagName == "span" || kw_o.tagName == "SPAN") {
			kws.push(kw_o.childNodes[0].data);
		}
	}
	kws_p_o = kws_o.parentNode;
	kws_p_o.removeChild(kws_o);
	for(i = 0; i < kws.length; i += 6) {
		tb_c = [];
		for(j = 0; j < 6; j++) {
			if((i + j) >= kws.length) {
				txt_o = document.createTextNode("");
				tb_c.push(txt_o);
			} else {
				txt_o = document.createTextNode(kws[i + j]);
				a_o = document.createElement('a');
				a_o.setAttribute("href", "''')
            odata = data.setdefault('gingin_url', {})
            self.ofo.write(self._esc_comm(odata))
            self.ofo.write('''/show_kw_docs/" + kws[i + j]);
				a_o.appendChild(txt_o);
				tb_c.push(a_o);
			}
		}
		tb.push(tb_c);
	}
	tb_o = create_table(tb);
	kws_p_o.appendChild(tb_o);
}

init_funcs.push(show_keywords);
-->
</script>

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

