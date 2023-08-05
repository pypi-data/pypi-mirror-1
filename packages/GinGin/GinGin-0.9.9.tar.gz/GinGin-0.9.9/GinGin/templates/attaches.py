# -*-: big5
from mez_xml.tools import nez_web

class attaches(nez_web):
    def __init__(self, ofo):
        super(attaches, self).__init__()
        self.ofo = ofo
        pass
    
    def _root(self, pdata, cdata):
        def temp(data):
            self.ofo.write('''<div id="content">

<div class="title">附加資料
<a href="''')
            odata = data.setdefault('gingin_url', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write('''/show_id_doc/''')
            odata = data.setdefault('doc_id', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write('''">
''')
            odata = data.setdefault('doc_id', {})
            self.ofo.write(self._esc_text(odata))
            self.ofo.write('''
</a>
號文章
</div>
<table>
''')
            cdata = data.setdefault('attaches', {})
            self.attaches(data, cdata)
            self.ofo.write('''

<tr><td>共 ''')
            odata = data.setdefault('num_attaches', {})
            self.ofo.write(self._esc_text(odata))
            self.ofo.write(''' 筆</td><td> </td></tr>

</table>
<br></br>
<br></br>
<form action="''')
            odata = data.setdefault('gingin_url', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write('''" method="post" enctype="multipart/form-data">
<input type="hidden" name="func" value="add_afile"></input>
<input type="hidden" id="add_doc_id" value="''')
            odata = data.setdefault('doc_id', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write('''" name="doc_id"></input>
<div class="title">新增附加資料</div>
<table>

<tr><td>索引字:</td>
<td><input type="text" name="afkey"></input></td></tr>
<tr><td>檔案:</td>

<td>
<input type="file" name="afile"></input>
</td></tr>
<tr><td> </td>
<td>
<input type="submit" value="上傳"></input>
</td></tr>
</table>
</form>

<form action="''')
            odata = data.setdefault('gingin_url', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write('''" method="post" id="del_form">
<input type="hidden" name="func" value="del_afile"></input>
<input type="hidden" id="del_doc_id" value="''')
            odata = data.setdefault('doc_id', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write('''" name="doc_id"></input>
<input type="hidden" id="del_afkey" name="afkey"></input>
</form>

</div>''')
            pass
        self._feed_subtree(temp, pdata, cdata)
        pass
    
    def attaches(self, pdata, cdata):
        def temp(data):
            self.ofo.write('''<tr ezid="attaches"><td>
<a href="''')
            odata = data.setdefault('gingin_url', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write('''/get_afile/''')
            odata = data.setdefault('doc_id', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write('''/''')
            odata = data.setdefault('afkey', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write('''">
''')
            odata = data.setdefault('afkey', {})
            self.ofo.write(self._esc_text(odata))
            self.ofo.write('''
</a>
</td><td><input type="button" value="刪除" onclick="del_afile(\'''')
            odata = data.setdefault('afkey', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write('''')"></input></td></tr>''')
            pass
        self._feed_subtree(temp, pdata, cdata)
        pass
    
    pass

