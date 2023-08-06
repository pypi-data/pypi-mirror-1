# -*-: big5
from mez_xml.tools import nez_web

class tb_view(nez_web):
    def __init__(self, ofo):
        super(tb_view, self).__init__()
        self.ofo = ofo
        pass
    
    def _root(self, pdata, cdata):
        def temp(data):
            self.ofo.write('''<html>
<head>
<link href="''')
            odata = data.setdefault('base_url', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write('''/GinGin.css" rel="stylesheet"></link>
<meta value="text/html; charset=big5" http-equiv="Content-Type"></meta>
<script src="''')
            odata = data.setdefault('base_url', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write('''/js/GinGin.js"></script>
</head>
''')
            cdata = data.setdefault('content', {})
            self.content(data, cdata)
            self.ofo.write('''
</html>''')
            pass
        self._feed_subtree(temp, pdata, cdata)
        pass
    
    def content(self, pdata, cdata):
        def temp(data):
            self.ofo.write('''<body ezid="content">
<div id="tb_view">
<table cellpadding="0" cellspacing="0" id="note">
<tr style="line-height: 0px">
<td><img src="''')
            odata = data.setdefault('base_url', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write('''images/green_box/luc.jpg"></img></td>
<td background="''')
            odata = data.setdefault('base_url', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write('''images/green_box/ub.jpg"></td>
<td><img src="''')
            odata = data.setdefault('base_url', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write('''images/green_box/ruc.jpg"></img></td>
</tr>
<tr>
<td style="background-repeat: repeat-y;" background="''')
            odata = data.setdefault('base_url', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write('''images/green_box/lb.jpg"></td>
<td width="100%">
   <div class="title">''')
            odata = data.setdefault('title', {})
            self.ofo.write(self._esc_text(odata))
            self.ofo.write('''</div>
   若是要引用此文，請用網址:
	<a href="''')
            odata = data.setdefault('base_url', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write('''GinGin_TB.py/trackback/''')
            odata = data.setdefault('doc_id', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write('''">
	''')
            odata = data.setdefault('base_url', {})
            self.ofo.write(self._esc_text(odata))
            self.ofo.write('''GinGin_TB.py/trackback/''')
            odata = data.setdefault('doc_id', {})
            self.ofo.write(self._esc_text(odata))
            self.ofo.write('''
	</a>
</td>
<td style="background-repeat: repeat-y;" background="''')
            odata = data.setdefault('base_url', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write('''images/green_box/rb.jpg"></td>
</tr>
<tr style="line-height: 0px">
<td>
<img src="''')
            odata = data.setdefault('base_url', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write('''images/green_box/lbc.jpg"></img></td>
<td style="background-repeat: repeat-x;" background="''')
            odata = data.setdefault('base_url', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write('''images/green_box/bb.jpg"></td>
<td><img src="''')
            odata = data.setdefault('base_url', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write('''images/green_box/rbc.jpg"></img></td>
</tr>
</table>

<!-- all trackbacks of the page -->
<p>
   引用文章 [<a href="''')
            odata = data.setdefault('link', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write('''">''')
            odata = data.setdefault('title', {})
            self.ofo.write(self._esc_text(odata))
            self.ofo.write('''</a>]
   所有網頁:
   <ul>
   ''')
            cdata = data.setdefault('pings', {})
            self.pings(data, cdata)
            self.ofo.write('''
   </ul>
   總共 ''')
            odata = data.setdefault('num_pings', {})
            self.ofo.write(self._esc_text(odata))
            self.ofo.write(''' 筆
</p>
</div>
   
</body>''')
            pass
        self._feed_subtree(temp, pdata, cdata)
        pass
    
    def pings(self, pdata, cdata):
        def temp(data):
            self.ofo.write('''<li ezid="pings">
   <a href="''')
            odata = data.setdefault('url', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write('''">''')
            odata = data.setdefault('title', {})
            self.ofo.write(self._esc_text(odata))
            self.ofo.write('''</a>
   </li>''')
            pass
        self._feed_subtree(temp, pdata, cdata)
        pass
    
    pass

