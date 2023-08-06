# -*-: big5
from mez_xml.tools import nez_web

class last_comments(nez_web):
    def __init__(self, ofo):
        super(last_comments, self).__init__()
        self.ofo = ofo
        pass
    
    def _root(self, pdata, cdata):
        def temp(data):
            self.ofo.write('''<div id="content">

<div class="title">
Last Comments
</div>

<div class="text">

''')
            cdata = data.setdefault('comments', {})
            self.comments(data, cdata)
            self.ofo.write('''

</div>

</div>''')
            pass
        self._feed_subtree(temp, pdata, cdata)
        pass
    
    def comments(self, pdata, cdata):
        def temp(data):
            self.ofo.write('''<div ezid="comments" class="comment">
<div class="''')
            odata = data.setdefault('pdate', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write('''">on ''')
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
<div class="msg">''')
            odata = data.setdefault('msg', {})
            self.ofo.write(self._esc_text(odata))
            self.ofo.write('''</div>
<div class="control">
<a href="''')
            odata = data.setdefault('gingin_url', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write('''/edit_comment/''')
            odata = data.setdefault('doc_id', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write('''">reply</a>
<a href="''')
            odata = data.setdefault('gingin_url', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write('''/show_id_doc/''')
            odata = data.setdefault('doc_id', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write('''">goto</a>
</div>
</div>''')
            pass
        self._feed_subtree(temp, pdata, cdata)
        pass
    
    pass

