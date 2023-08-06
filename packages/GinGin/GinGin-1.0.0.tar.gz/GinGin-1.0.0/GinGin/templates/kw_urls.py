# -*-: big5
from mez_xml.tools import nez_web

class kw_urls(nez_web):
    def __init__(self, ofo):
        super(kw_urls, self).__init__()
        self.ofo = ofo
        pass
    
    def _root(self, pdata, cdata):
        def temp(data):
            self.ofo.write('''<div class="content">
<div class="title">
關鍵字 ''')
            odata = data.setdefault('name', {})
            self.ofo.write(self._esc_text(odata))
            self.ofo.write('''
共有 ''')
            odata = data.setdefault('url_cnt', {})
            self.ofo.write(self._esc_text(odata))
            self.ofo.write(''' 個 URL:
</div>

<div class="text">
<form action="''')
            odata = data.setdefault('gingin_url', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write('''" method="post">
<dl>
''')
            cdata = data.setdefault('urls', {})
            self.urls(data, cdata)
            self.ofo.write('''
</dl>
<input type="hidden" name="func" value="del_kw_urls"></input>
<input type="hidden" name="keyword" value="''')
            odata = data.setdefault('name', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write('''"></input>
<input type="submit" value="刪除"></input>
</form>
</div>
</div>''')
            pass
        self._feed_subtree(temp, pdata, cdata)
        pass
    
    def urls(self, pdata, cdata):
        def temp(data):
            self.ofo.write('''<dt ezid="urls">
<input type="checkbox" name="url_id" value="''')
            odata = data.setdefault('id', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write('''"></input>
<a href="''')
            odata = data.setdefault('url', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write('''">''')
            odata = data.setdefault('title', {})
            self.ofo.write(self._esc_text(odata))
            self.ofo.write('''</a>
- ''')
            odata = data.setdefault('creator', {})
            self.ofo.write(self._esc_text(odata))
            self.ofo.write('''
<a href="''')
            odata = data.setdefault('gingin_url', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write('''/edit_url/''')
            odata = data.setdefault('id', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write('''">[edit]</a>
''')
            cdata = data.setdefault('abstracts', {})
            self.abstracts(data, cdata)
            self.ofo.write('''
</dt>''')
            pass
        self._feed_subtree(temp, pdata, cdata)
        pass
    
    def abstracts(self, pdata, cdata):
        def temp(data):
            self.ofo.write('''<dd ezid="abstracts">
''')
            odata = data.setdefault('abstract', {})
            self.ofo.write(self._esc_text(odata))
            self.ofo.write('''
</dd>''')
            pass
        self._feed_subtree(temp, pdata, cdata)
        pass
    
    pass

