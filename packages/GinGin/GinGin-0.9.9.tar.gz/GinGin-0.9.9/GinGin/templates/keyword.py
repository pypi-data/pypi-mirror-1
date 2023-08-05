# -*-: big5
from mez_xml.tools import nez_web

class keyword(nez_web):
    def __init__(self, ofo):
        super(keyword, self).__init__()
        self.ofo = ofo
        pass
    
    def _root(self, pdata, cdata):
        def temp(data):
            self.ofo.write('''<div id="content">

<div class="title">
關鍵字 ''')
            odata = data.setdefault('name', {})
            self.ofo.write(self._esc_text(odata))
            self.ofo.write('''
</div>
相關文件:

<div class="text">
<table>
<tr><th>主題</th><th>作者</th><th>修改日期</th></tr>
  ''')
            cdata = data.setdefault('docs', {})
            self.docs(data, cdata)
            self.ofo.write('''
</table>
</div>
<br></br>
外部 URL:

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
    
    def docs(self, pdata, cdata):
        def temp(data):
            self.ofo.write('''<tr ezid="docs">
    <td>
      <a href="''')
            odata = data.setdefault('gingin_url', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write('''/show_id_doc/''')
            odata = data.setdefault('doc_id', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write('''">
      ''')
            odata = data.setdefault('title', {})
            self.ofo.write(self._esc_text(odata))
            self.ofo.write('''
      </a>
    </td>
    <td>
      ''')
            odata = data.setdefault('creator', {})
            self.ofo.write(self._esc_text(odata))
            self.ofo.write('''
    </td>
    <td>
      ''')
            odata = data.setdefault('pdate', {})
            self.ofo.write(self._esc_text(odata))
            self.ofo.write('''
    </td>
  </tr>''')
            pass
        self._feed_subtree(temp, pdata, cdata)
        pass
    
    def urls(self, pdata, cdata):
        def temp(data):
            self.ofo.write('''<dt ezid="urls">
<input type="checkbox" name="url_id" value="''')
            odata = data.setdefault('url_id', {})
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
            odata = data.setdefault('url_id', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write('''">[edit]</a>
<dd>
''')
            odata = data.setdefault('abstract', {})
            self.ofo.write(self._esc_text(odata))
            self.ofo.write('''
</dd>
</dt>''')
            pass
        self._feed_subtree(temp, pdata, cdata)
        pass
    
    pass

