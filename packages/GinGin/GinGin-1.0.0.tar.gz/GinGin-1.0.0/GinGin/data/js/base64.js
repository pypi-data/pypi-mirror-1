var base64 = {
    _b64str: "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=",
    
    encode: function(input) {
	var output = "";
	var c1, c2, c3;
	var enc1, enc2, enc3, enc4;
	var i;
	
	for(i = 0; i < input.length;) {
	    c1 = input.charCodeAt(i++);
	    c2 = input.charCodeAt(i++);
	    c3 = input.charCodeAt(i++);
	    
	    enc1 = c1 >> 2;
	    enc2 = ((c1 & 0x3) << 4) | (c2 >> 4);
	    enc3 = ((c2 & 0xf) << 2) | (c3 >> 6);
	    enc4 = c3 & 0x3f;
	    
	    if(isNaN(c2)) enc3 = 64;
	    if(isNaN(c3)) enc4 = 64;
	    output = output + this._b64str.charAt(enc1) +
		this._b64str.charAt(enc2) + this._b64str.charAt(enc3) +
		this._b64str.charAt(enc4);
	    
	    return output;
	}
    },
    
    decode: function(input) {
	var output = "";
	var enc1, enc2, enc3;
	var c1, c2, c3;
	var i;
	
	for(i = 0; i < input.length;) {
	    enc1 = this._b64str.indexOf(input[i++]);
	    enc2 = this._b64str.indexOf(input[i++]);
	    enc3 = this._b64str.indexOf(input[i++]);
	    enc4 = this._b64str.indexOf(input[i++]);
	    
	    c1 = (enc1 << 2) | (enc2 >> 4);
	    c2 = ((enc2 & 0xf) << 4) | (enc3 >> 2);
	    c3 = ((enc3 & 0x3) << 6) | enc4;
	    
	    output = output + String.fromCharCode(c1);
	    if(enc3 != 64) output = output + String.fromCharCode(c2);
	    if(enc4 != 64) output = output + String.fromCharCode(c3);
	}
	return output;
    }
}
