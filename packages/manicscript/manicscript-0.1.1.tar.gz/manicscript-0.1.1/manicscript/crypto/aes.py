from base64 import b64encode, b64decode
import Crypto.Cipher.AES as AES
from hashlib import md5
from secrand import SecureRandom

rand = SecureRandom()

class SaltNotFoundException(Exception):
        pass

def keygen(passphrase, salt, keybits=128):
        MITER = 3

        # Prepare the hash
        seed = passphrase + salt
        keysource = []

        hash = ''
        for i in range(MITER):
                hash = md5(hash + seed).digest()
                keysource.append(hash)

        # Extract key data
        if keybits == 128:
                key = keysource[0]
                iv = keysource[1]
        elif keybits == 192:
                key = keysource[0] + keysource[1][:8]
                iv = keysource[2]
        elif keybits == 256:
                key = keysource[0] + keysource[1]
                iv = keysource[2]

        # Operation Complete!
        return key, iv

def desalt(ciphertext, saltbits=64):
        if not ciphertext.startswith('Salted__'):
                raise SaltNotFoundException
        saltbytes = saltbits / 8
        salt = ciphertext[8:8+saltbytes]
        ciphertext = ciphertext[8+saltbytes:]
        return salt, ciphertext

def encoder(passphrase, salt=None, saltbits=64, keybits=128):
        # Prepare salt
        if salt is None:
                salt = ''.join([chr(rand.randint(0,255)) for i in range(saltbits/8)])

        # Prepare cipher
        key, iv = keygen(passphrase, salt, keybits=keybits)
        aes = AES.new(key, AES.MODE_CBC, iv)
        return salt, aes

def decoder(passphrase, salt, keybits=128):
        # Prepare cipher
        key, iv = keygen(passphrase, salt, keybits=keybits)
        aes = AES.new(key, AES.MODE_CBC, iv)
        return aes

def openssl_encode(plaintext, passphrase, salt=None, saltbits=64, keybits=128, padding=0x08, binmode=False, **opts):
        bsize = AES.block_size
        if not binmode: plaintext = plaintext.encode('utf-8')
        plaintext += chr(padding) * (-len(plaintext) % bsize)
        salt, aes = encoder(passphrase, salt, saltbits, keybits)

        ciphertext = ''
        for i in range(len(plaintext)/bsize):
                ciphertext += aes.encrypt(plaintext[i*bsize:(i+1)*bsize])

        return b64encode('Salted__' + salt + ciphertext)

def openssl_decode(ciphertext, passphrase, saltbits=64, keybits=128, padding=0x08, binmode=False, **opts):
        bsize = AES.block_size
        ciphertext = b64decode(ciphertext)
        salt, ciphertext = desalt(ciphertext, saltbits)
        aes = decoder(passphrase, salt, keybits)

        plaintext = ''
        for i in range(len(ciphertext)/bsize):
                plaintext += aes.decrypt(ciphertext[i*bsize:(i+1)*bsize])
        plaintext = plaintext.rstrip(chr(padding))
        if not binmode: plaintext = unicode( plaintext, 'utf-8')
        return plaintext
