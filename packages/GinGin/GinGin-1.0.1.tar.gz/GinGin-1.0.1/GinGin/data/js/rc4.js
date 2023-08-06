
function rc4(key) {
    var sbox = new Array();
    var i, j, klen;
    
    this.key = key;
    this.i = this.j = 0;
    this.sbox = sbox;
    klen = key.length;
    for(i = 0; i < 256; i++) {
	sbox.push(i);
    }
    for(i = j = 0; i < 256; i++) {
	j = (j + sbox[i] + key[i % klen]) % 256;
	this.swap(i, j);
    }
}

rc4.prototype.swap = function(i, j) {
    var m;
    
    m = this.sbox[i];
    this.sbox[i] = this.sbox[j];
    this.sbox[j] = m;
}

rc4.prototype.get_random = function() {
    var i, j, t;
    
    i = this.i;
    j = this.j;
    
    i = (i + 1) % 256;
    j = (j + this.sbox[i]) % 256;
    
    this.swap(i, j);
    
    t = (this.sbox[i] + this.sbox[j]) % 256;
    this.i = i;
    this.j = j;
    
    return t;
}

rc4.prototype.encrypt = function(plain) {
    var cipher = new Array();
    var i, plen;
    
    plen = plain.length;
    for(i = 0; i < plen; i++) {
	cipher.push(this.get_random() ^ plain[i]);
    }
    return cipher;
}
