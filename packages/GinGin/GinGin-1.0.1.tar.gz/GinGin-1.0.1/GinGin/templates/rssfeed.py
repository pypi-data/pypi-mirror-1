# -*-: big5
from mez_xml.tools import nez_web

class rssfeed(nez_web):
    def __init__(self, ofo):
        super(rssfeed, self).__init__()
        self.ofo = ofo
        pass
    
    def _root(self, pdata, cdata):
        def temp(data):
            self.ofo.write('''<rss version="2.0" xmlns:dc="http://purl.org/dc/elements/1.1/">
<channel>
	<title>''')
            odata = data.setdefault('title', {})
            self.ofo.write(self._esc_text(odata))
            self.ofo.write('''</title>
	<link>''')
            odata = data.setdefault('gingin_url', {})
            self.ofo.write(self._esc_text(odata))
            self.ofo.write('''</link>
	<dc:language></dc:language>
	<dc:creator>''')
            odata = data.setdefault('site', {})
            self.ofo.write(self._esc_text(odata))
            self.ofo.write('''</dc:creator>
	<dc:date></dc:date>
	''')
            cdata = data.setdefault('content', {})
            cdata = cdata.setdefault('feeds', {})
            cdata = cdata.setdefault('feed', {})
            self.feed(data, cdata)
            self.ofo.write('''
</channel>
</rss>''')
            pass
        self._feed_subtree(temp, pdata, cdata)
        pass
    
    def feed(self, pdata, cdata):
        def temp(data):
            self.ofo.write('''<item ezid="content.feeds.feed">
		<title>''')
            odata = data.setdefault('title', {})
            self.ofo.write(self._esc_text(odata))
            self.ofo.write('''</title>
		<link>''')
            odata = data.setdefault('gingin_url', {})
            self.ofo.write(self._esc_text(odata))
            self.ofo.write('''/show_id_doc/''')
            odata = data.setdefault('doc_id', {})
            self.ofo.write(self._esc_text(odata))
            self.ofo.write('''</link>
		<description>''')
            odata = data.setdefault('abs', {})
            self.ofo.write(self._esc_text(odata))
            self.ofo.write('''</description>
		<guid>''')
            odata = data.setdefault('gingin_url', {})
            self.ofo.write(self._esc_text(odata))
            self.ofo.write('''/show_id_doc/''')
            odata = data.setdefault('doc_id', {})
            self.ofo.write(self._esc_text(odata))
            self.ofo.write('''</guid>
		<dc:date>''')
            odata = data.setdefault('pdate', {})
            self.ofo.write(self._esc_text(odata))
            self.ofo.write('''</dc:date>
	</item>''')
            pass
        self._feed_subtree(temp, pdata, cdata)
        pass
    
    pass

