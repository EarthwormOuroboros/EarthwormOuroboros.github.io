/usr/bin/env python3

import argpars
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP

code = 'nooneknows'
private_key_file = '.keys/rsa_private.key'
public_key_file = '.keys/rsa_public.pem'

parser = argparse.ArgumentParser()
parser.add_argument("-k","--keyfile",action="store_true",
                    help="Create key file pair")
parser.add_argument("-f","--fetch",action="store_true",
                    help="Fetch data")
parser.add_argument("-s","--set",action="store_true",
                    help="Set data.")


def gen-key():
    key = RSA.generate(2048)
    encrypted_key = key.exportKey(passphrase=code, pkcs=8, protection="scryptAndAES128-CBC")
    with open(private_key_file, 'wb') as f: f.write(encrypted_key)
    with open(public_key_file, 'wb') as f: f.write(key.publickey().exportKey())


def encrypt-string():
    recipient_key = RSA.import_key(open(public_key_file).read())
    session_key = get_random_bytes(16)

    cipher_rsa = PKCS1_OAEP.new(recipient_key)

    cipher_aes = AES.new(session_key, AES.MODE_EAX)
    data = b'blah blah blah Python blah blah'
    ciphertext, tag = cipher_aes.encrypt_and_digest(data)


def decrypt-string():
    
    with open('/path/to/encrypted_data.bin', 'rb') as fobj:
        private_key = RSA.import_key(
            open(private_key_file).read(),
            passphrase=code)
 
        enc_session_key, nonce, tag, ciphertext = [ fobj.read(x) 
                                                    for x in (private_key.size_in_bytes(), 
                                                    16, 16, -1) ]
 
        cipher_rsa = PKCS1_OAEP.new(private_key)
        session_key = cipher_rsa.decrypt(enc_session_key)
 
        cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
        data = cipher_aes.decrypt_and_verify(ciphertext, tag)
 
    print(data)

def main():



main()
