# -*-: big5
from mez_xml.tools import nez_web

class tb_rss(nez_web):
    def __init__(self, ofo):
        super(tb_rss, self).__init__()
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
 <error>0</error>
 <rss version="0.91">
  <channel>
   <title>''')
            odata = data.setdefault('title', {})
            self.ofo.write(self._esc_text(odata))
            self.ofo.write('''</title>
   <link>''')
            odata = data.setdefault('link', {})
            self.ofo.write(self._esc_text(odata))
            self.ofo.write('''</link>
   <description>''')
            odata = data.setdefault('description', {})
            self.ofo.write(self._esc_text(odata))
            self.ofo.write('''</description>
   <language>''')
            odata = data.setdefault('language', {})
            self.ofo.write(self._esc_text(odata))
            self.ofo.write('''</language>
   
   ''')
            cdata = data.setdefault('items', {})
            self.items(data, cdata)
            self.ofo.write('''
   
  </channel>
 </rss>
</response>''')
            pass
        self._feed_subtree(temp, pdata, cdata)
        pass
    
    def items(self, pdata, cdata):
        def temp(data):
            self.ofo.write('''<item ezid="items">
    <title>''')
            odata = data.setdefault('title', {})
            self.ofo.write(self._esc_text(odata))
            self.ofo.write('''</title>
    <link>''')
            odata = data.setdefault('link', {})
            self.ofo.write(self._esc_text(odata))
            self.ofo.write('''</link>
    <description>''')
            odata = data.setdefault('description', {})
            self.ofo.write(self._esc_text(odata))
            self.ofo.write('''</description>
   </item>''')
            pass
        self._feed_subtree(temp, pdata, cdata)
        pass
    
    pass

