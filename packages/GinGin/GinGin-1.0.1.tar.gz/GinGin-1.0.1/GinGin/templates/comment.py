# -*-: big5
from mez_xml.tools import nez_web

class comment(nez_web):
    def __init__(self, ofo):
        super(comment, self).__init__()
        self.ofo = ofo
        pass
    
    def _root(self, pdata, cdata):
        def temp(data):
            self.ofo.write('''<div id="comment">

<div class="title">¯d¨¥: ¤å³¹ ''')
            odata = data.setdefault('doc_id', {})
            self.ofo.write(self._esc_text(odata))
            self.ofo.write('''</div>
<form action="''')
            odata = data.setdefault('gingin_url', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write('''" onsubmit="javascript:return nospam()" method="get">
<input type="hidden" name="func" value="add_comment"></input>
<input type="hidden" name="doc_id" value="''')
            odata = data.setdefault('doc_id', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write('''"></input>
<input type="hidden" name="key" id="key"></input>
<table>
<tr><td><input accesskey="N" maxlength="60" type="text" name="name" size="20"></input>*Name(N)</td></tr>
<tr><td><input accesskey="M" maxlength="60" type="text" name="email" size="20"></input>*Mail(M)</td></tr>
<tr><td><input accesskey="W" maxlength="60" type="text" name="website" size="20"></input>Website(W)</td></tr>
<tr><td><textarea accesskey="C" rows="5" cols="40" id="msg" name="msg">comment...(C)</textarea></td></tr>
</table>
<input accesskey="S" type="submit" value="Save(S)"></input>
<span id="working">+</span>
</form>
<script src="''')
            odata = data.setdefault('base_url', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write('''/js/rc4.js" language="Javascript">
var dummy;
</script>
<script language="Javascript">
var plain = "''')
            odata = data.setdefault('attack_plain', {})
            self.ofo.write(self._esc_text(odata))
            self.ofo.write('''";
var cipher = "''')
            odata = data.setdefault('attack_cipher', {})
            self.ofo.write(self._esc_text(odata))
            self.ofo.write('''";
</script>
<script src="''')
            odata = data.setdefault('base_url', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write('''/js/base64.js" language="Javascript">
var dummy;
</script>
<script src="''')
            odata = data.setdefault('base_url', {})
            self.ofo.write(self._esc_param(odata))
            self.ofo.write('''/js/antispam.js" language="Javascript">
var dummy;
</script>

</div>''')
            pass
        self._feed_subtree(temp, pdata, cdata)
        pass
    
    pass

