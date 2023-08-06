# Load logging framework
import logging
logger = logging.getLogger(__name__)

# Load JSON
from django.utils import simplejson

# Load crypto methods
from manicscript.crypto.aes import openssl_encode, openssl_decode
from manicscript.crypto.secrand import SecureRandom
rand = SecureRandom(paranoid = False)

from hashlib import md5

# Load errors
from .assertions import InvalidMessageDecode, InvalidMessageVerify, InvalidMessageEncode

# FIXME: multimessage_* should use the safe_sign/safe_verify algorithm

def message_decode(ctxt, secret, opts={'keybits': 256,}):
        # Set binary encoding mode
        opts = opts.copy()
        opts['binmode'] = True

        m = md5()
        ptxt = openssl_decode(ctxt, secret, **opts)
        jmsg = ptxt[m.digest_size:]
        hash = ptxt[:m.digest_size]
        m.update(jmsg)
        hmsg = m.digest()
        if hmsg != hash:
                raise InvalidMessageVerify
        return jmsg

def message_encode(jmsg, secret, opts={'keybits': 256,}):
        # Set binary encoding mode
        opts = opts.copy()
        opts['binmode'] = True

        hash = md5(jmsg).digest()
        ctxt = openssl_encode( hash + jmsg, secret, **opts)
        return ctxt

def multimessage_encode(msg_pub, msg_prv, secrets, opts={'keybits': 256, 'saltbytes': 16,}):
        """Encode a message that has both a public and a private portion"""
        try:
                jmsg_pub = simplejson.dumps(msg_pub).encode('utf-8')
                jmsg_prv = simplejson.dumps(msg_prv).encode('utf-8')
        except:
                raise InvalidMessageEncode

        cmsg = { '_pub': jmsg_pub, '_multi_prv': {} }

        for k, secret in secrets.items():
                sigpack = pack_safesign( jmsg_pub, jmsg_prv, saltbytes=opts['saltbytes'])
                cmsg['_multi_prv'][k] = message_encode(sigpack, secret, opts=opts)

        return cmsg

def multimessage_peek(cmsg):
        """Peek at the public portion of a multimessage"""
        # Extract the public message
        try:
                jmsg_pub = cmsg['_pub']
                msg_pub = simplejson.loads(jmsg_pub)
        except:
                raise InvalidMessageDecode

        return msg_pub

def multimessage_decode(cmsg, handle, secret, opts={'keybits': 256, 'saltbytes': 16,}):
        """Fully decrypt the contents of a multimessage"""
        # Attempt to extract the encrypted message
        sigpack = message_decode(cmsg['_multi_prv'][handle], secret, opts=opts)

        # Extract the message components
        jmsg_pub = cmsg['_pub']
        jmsg_prv = unpack_safesign(cmsg['_pub'], sigpack, saltbytes=opts['saltbytes'])

        # Parse message components
        try:
                msg_pub = simplejson.loads(unicode( jmsg_pub, 'utf-8'))
                msg_prv = simplejson.loads(unicode( jmsg_prv, 'utf-8'))
        except:
                raise InvalidMessageDecode

        # Operation Complete!
        return msg_pub, msg_prv

def pack_safesign(pub, prv, saltbytes=16):
        """Sign a message securely.  This returns (salt, hash(salt . pub), prv),
           which should be encrypted using a shared secret at some point.
           By using hash(salt . msg) instead of hash(msg), a successful attack
           on the hash for one signature does not grant an attack for the same
           message on other signatures. Also, the presentation of multiple
           signatures using the same message but different secrets does not
           present a risk for differential analysis. Price: entropy."""
        # Prepare a salt for this signature
        salt = ''.join([chr(rand.randint(0,255)) for i in range(saltbytes)])

        # Apply the salt
        m = md5(salt)
        m.update(pub)

        # Return the signature pack
        return salt + m.digest() + prv

def unpack_safesign(pub, sigpack, saltbytes=16):
        # Extract the salt and signature hash
        salt = sigpack[:saltbytes]
        sigpack = sigpack[saltbytes:]

        # Compute the hash
        h = md5(salt)
        hash = sigpack[:h.digest_size]
        sigpack = sigpack[h.digest_size:]
        h.update(pub)

        # Extract the private region
        prv = sigpack

        # Raise an exception on signature mismatches
        if h.digest() != hash:
                raise InvalidMessageVerify

        # Compare hashes
        return prv

def safe_sign(msg, secret, opts={'keybits': 256, 'saltbytes': 16}):
        # Set binary encoding mode
        opts = opts.copy()
        opts['binmode'] = True

        # Get the signature pack
        sigpack = pack_safesign(msg, '', saltbytes=opts['saltbytes'])

        # Sign the message
        return openssl_encode( sigpack, secret, **opts)

def safe_verify(sig, msg, secret, opts={'keybits': 256, 'saltbytes': 16}):
        # Set binary encoding mode
        opts = opts.copy()
        opts['binmode'] = True

        # Decrypt the signature
        ptxt = openssl_decode( sig, secret, **opts)

        # 

