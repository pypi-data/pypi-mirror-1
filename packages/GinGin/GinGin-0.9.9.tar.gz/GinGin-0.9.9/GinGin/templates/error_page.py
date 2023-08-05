# -*-: big5
from mez_xml.tools import nez_web

class error_page(nez_web):
    def __init__(self, ofo):
        super(error_page, self).__init__()
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
            self.ofo.write('''<html ezid="content">
<head>
	<title>''')
            odata = data.setdefault('host', {})
            self.ofo.write(self._esc_text(odata))
            self.ofo.write('''</title>
<style>
<!--
*	{
	font-size:	12pt;
}

.title {
        font-size:      18pt;
        font-weight:    700; 
}
.error {
        margin-left:    20px;
        border-style:   solid;
        border-width:   1px;
        border-color:   #005A9C;
        padding:        2px 5px 2px 5px;
	background-color:	#ffcc33;
	width:		80%;
}
-->
</style>
</head>
<body>
<div class="title">ERROR</div>
<div class="error">
<pre>
''')
            odata = data.setdefault('error', {})
            self.ofo.write(self._esc_text(odata))
            self.ofo.write('''
</pre>
</div>
Please contact administrator!
</body>
</html>''')
            pass
        self._feed_subtree(temp, pdata, cdata)
        pass
    
    pass

