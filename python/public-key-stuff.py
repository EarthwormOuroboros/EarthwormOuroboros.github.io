#!/usr/bin/env python3

import argparse
from Crypto.Cipher import AES

# https://www.blog.pythonlibrary.org/2016/05/18/python-3-an-intro-to-encryption/

key = 'nooneknows'

parser = argparse.ArgumentParser()
parser.add_argument("-f","--fetch",action="store_true",
                    help="Fetch data")
parser.add_argument("-s","--set",action="store_true",
                    help="Set data.")

# Encryption
def encrypt_string(DATA, KEY, IV):
    encryption_suite = AES.new(KEY, AES.MODE_CBC, IV)
    cipher_text = encryption_suite.encrypt(DATA)
    return cipher_text


# Decryption
def decrypt_string(DATA, KEY, IV):
    decryption_suite = AES.new(KEY, AES.MODE_CBC, IV)
    plain_text = decryption_suite.decrypt(DATA)
    return plain_text


def main():
    iv = '1234567890abcdef'
    payload = 'Whut3v4!'
    
    enc_data = encrypt_string(payload, key, iv)
    enc_data
    
    dec_data = decrypt_string(enc_data, key, iv)
    dec_data

main()
