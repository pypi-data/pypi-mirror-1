# -*-: big5
from mez_xml.tools import nez_web

class unpublished(nez_web):
    def __init__(self, ofo):
        super(unpublished, self).__init__()
        self.ofo = ofo
        pass
    
    def _root(self, pdata, cdata):
        def temp(data):
            self.ofo.write('''<div id="content">

<div class="title">
未發佈文件:
</div>
<div class="text">
<table>
<tr><th>主題</th><th>作者</th><th>修改日期</th></tr>
  ''')
            cdata = data.setdefault('docs', {})
            self.docs(data, cdata)
            self.ofo.write('''
</table>
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
    
    pass

