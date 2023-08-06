var attack_len = 1;
var __ANTISPAM_MAX_ROUNDS = 20;
var __attack_wait = 200;

function cracker(plain, cipher) {
    var s_plain, s_cipher;
    var i_plain, i_cipher;
    var i;
    
    s_plain = base64.decode(plain);
    s_cipher = base64.decode(cipher);
    i_plain = new Array();
    for(i = 0; i < s_plain.length; i++) {
	i_plain.push(s_plain.charCodeAt(i));
    }
    
    i_cipher = new Array();
    for(i = 0; i < s_cipher.length; i++) {
	i_cipher.push(s_cipher.charCodeAt(i));
    }
    
    this.plain = i_plain;
    this.cipher = i_cipher;
    
    this.key = new Array();
    for(i = 0; i < attack_len; i++) {
	this.key.push(0);
    }
}

cracker.prototype.attack = function(round) {
    var rc4_o;
    var reverse;
    var i, cnt;
    var plain, cipher;
    
    plain = this.plain;
    cipher = this.cipher;
    key = this.key;
    
    cnt = 0;
    while(1) {
	if(cnt++ >= round && round != 0) return null;
	
	rc4_o = new rc4(key);
	reverse = rc4_o.encrypt(cipher);
	for(i = 0; i < plain.length; i++) {
	    if(reverse[i] != plain[i]) break;
	}
	if(i >= plain.length) break;
	
	for(i = 0; i < key.length; i++) {
	    key[i] = (key[i] + 1) % 256;
	    if(key[i] != 0) break;
	}
	if(i >= key.length) break;
    }
    
    return key;
}

function __clear_children(n) {
    var i;
    for(i = 0; i < n.childNodes.length; i++) {
	n.removeChild(n.childNodes.item(0));
    }
}

function start_attack() {
    var cracker_o = new cracker(plain, cipher);
    var tm_hdlr;
    var working_idx = 0;
    var working_str = "-\\|/";
    
    tm_hdlr = function() {
	var key, working = document.getElementById("working");
	var s_key, i, txt_o;
	
	key = cracker_o.attack(__ANTISPAM_MAX_ROUNDS);
	if(key != null) {
	    s_key = "";
	    for(i = 0; i < key.length; i++) {
		s_key = s_key + String.fromCharCode(key[i]);
	    }
	    document.getElementById("key").value = base64.encode(s_key);
	    __clear_children(working);
	    return;
	}
	__clear_children(working);
	txt_o = document.createTextNode(working_str.charAt(working_idx));
	working_idx = (working_idx + 1) % 4;
	working.appendChild(txt_o);
	window.setTimeout(tm_hdlr, __attack_wait);
    }
    tm_hdlr();
}

init_funcs.push(start_attack);

function nospam() {
    var key_o = document.getElementById("key");
    
    if(key_o.value) return true;
    __attack_wait = 0;
    alert("wait amonent!");
    if(key_o.value) return true;
    return false;
}
