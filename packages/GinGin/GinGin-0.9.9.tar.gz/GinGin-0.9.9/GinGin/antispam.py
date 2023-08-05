
class rc4:
    def __init__(self, key):
	self.key = key
	self.sbox = sbox = list(range(256))
	klen = len(key)
	j = 0
	for i in range(256):
	    j = (j + sbox[i] + key[i % klen]) % 256
	    sbox[i], sbox[j] = sbox[j], sbox[i]
	    pass
	self.i = self.j = 0
	pass
    
    def encrypt(self, plain):
	i = self.i
	j = self.j
	sbox = self.sbox
	
	cipher = []
	for idx in range(len(plain)):
	    i = (i + 1) % 256
	    j = (j + sbox[i]) % 256
	    
	    sbox[i], sbox[j] = sbox[j], sbox[i]
	    
	    t = (sbox[i] + sbox[j]) % 256
	    
	    cipher.append(t ^ plain[idx])
	    pass
	
	self.i = i
	self.j = j
	return cipher
    pass


def get_key(doc_id):
    import md5, array, config
    m = md5.md5(config.GINGIN_COMMENT_SECRET + str(doc_id))
    key = array.array('B', m.digest())[:1]
    return key


def gen_an_attack(key):
    import random
    rc4_o = rc4(key)
    plain = [int(random.random() * 256) for i in range(32)]
    cipher = rc4_o.encrypt(plain)
    return plain, cipher

if __name__ == '__main__':
    key = get_key(257)
    plain, cipher = gen_an_attack(key)
    print key
    print plain
    print cipher
    rc4_o = rc4(key)
    print rc4_o.encrypt(cipher)
    pass
