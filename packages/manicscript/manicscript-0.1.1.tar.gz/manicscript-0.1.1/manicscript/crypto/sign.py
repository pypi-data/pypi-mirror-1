from hmac import new as hmac
import hashlib
from django.utils import simplejson as json
from binascii import a2b_hex, b2a_hex, a2b_base64, b2a_base64

ALGS = {
        'HMAC': hmac,
}

HASHES = {
        'MD5': hashlib.md5,
        'SHA1': hashlib.sha1,
        'SHA224': hashlib.sha224,
        'SHA256': hashlib.sha256,
        'SHA384': hashlib.sha384,
        'SHA512': hashlib.sha512,
}

ENCS = {
        'RAW': (lambda x: x, lambda x: x),
        'HEX': (b2a_hex, a2b_hex),
        'BASE64': (b2a_base64, a2b_base64),
}



def jsonsign(key, msg, method='HMAC-SHA256-HEX'):
        alg, hash, enc = method.split('-')
        alg = ALGS[alg]
        hash = HASHES[hash]
        enc = ENCS[enc][0]
        msg = json.dumps(msg)

        sig = enc(alg(key, msg, hash).digest())

        return {'alg': method, 'msg': msg, 'sig': sig}

def jsonverify(key, signed_msg):
        method = signed_msg['alg']
        msg = signed_msg['msg']
        sig = signed_msg['sig']

        alg, hash, enc = method.split('-')
        alg = ALGS[alg]
        hash = HASHES[hash]
        enc = ENCS[enc][1]
        unpacked_msg = json.loads(msg)

        true_sig = alg(key, msg, hash).digest()
        
        return (enc(sig) == true_sig, unpacked_msg)
