#!/usr/bin/env python3

import argparse
from cryptography.fernet import Fernet

parser = argparse.ArgumentParser()
parser.add_argument("-f","--fetch",action="store_true",
                    help="Fetch data")
parser.add_argument("-s","--set",action="store_true",
                    help="Set data.")


def crypto_string(DATA, KEY, ACTION):
    cipher = Fernet(KEY)
    if ACTION == "encrypt":
        # Encryption
        data = cipher.encrypt(DATA)
    elif ACTION == 'decrypt':
        # Decryption
        data = cipher.decrypt(DATA)

    return data


def main():
    cipher_key = Fernet.generate_key()
    string = b'Whut3v4Mang!'

    encrypted_text = crypto_string(string, cipher_key, 'encrypt')
    print(encrypted_text)

    decrypted_text = crypto_string(encrypted_text, cipher_key, 'decrypt')
    print(decrypted_text)


main()

