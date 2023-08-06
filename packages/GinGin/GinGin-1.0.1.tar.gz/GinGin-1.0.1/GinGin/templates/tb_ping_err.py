# -*-: big5
from mez_xml.tools import nez_web

class tb_ping_err(nez_web):
    def __init__(self, ofo):
        super(tb_ping_err, self).__init__()
        self.ofo = ofo
        pass
    
    def _root(self, pdata, cdata):
        def temp(data):
            self.ofo.write('''''')
            cdata = data.setdefault('content', {})
            self.content(data, cdata)
            self.ofo.write('''''')
            pass
        self._feed_subtree(temp, pdata, cdata)
        pass
    
    def content(self, pdata, cdata):
        def temp(data):
            self.ofo.write('''<response ezid="content">
<error>''')
            odata = data.setdefault('ecode', {})
            self.ofo.write(self._esc_text(odata))
            self.ofo.write('''</error>
''')
            cdata = data.setdefault('msg', {})
            self.msg(data, cdata)
            self.ofo.write('''
</response>''')
            pass
        self._feed_subtree(temp, pdata, cdata)
        pass
    
    def msg(self, pdata, cdata):
        def temp(data):
            self.ofo.write('''<message ezid="msg">''')
            odata = data.setdefault('data', {})
            self.ofo.write(self._esc_text(odata))
            self.ofo.write('''</message>''')
            pass
        self._feed_subtree(temp, pdata, cdata)
        pass
    
    pass

