#!/usr/bin/env python3

import os,argparse
from cryptography.fernet import Fernet
from datetime import date, datetime, timedelta

parser = argparse.ArgumentParser()
parser.add_argument("-f","--decrypt",action="store_true",
                    help="Fetch data")
parser.add_argument("-s","--encrypt",action="store_true",
                    help="Set data.")

args = parser.parse_args()

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
    now = datetime.now()

    add_data = ("INSERT INTO ds389 "
                "(edata, date, time) "
                "VALUES (%s, %s, %s)")
    read_data = ("SELECT FROM ds389 "
                 "(edata, date, time) "
                 "VALUES (%(emp_no)s, %(salary)s, %(from_date)s, %(to_date)s)")


    if args.encrypt:
      password = 'Whut3v4Mang!'
      string = bytes.encode(password)
      cipher_key = Fernet.generate_key()
      key_file = os.path.expanduser('~') + os.sep + '.iok'

      try:
        f = open(key_file, 'wt').write(bytes.decode(cipher_key))

      except IOError:
        print ('Could not open key file: ' + key_file)
        print ('Bye!!!')
        sys.exit()

      encrypted_text = crypto_string(string, cipher_key, 'encrypt')
      print(encrypted_text)

      data = (encrypted_text, now.strftime('%Y-%m-%d'), now.strftime('%H:%M:%S'))


    if args.decrypt:
      key_file = os.path.expanduser('~') + os.sep + '.iok'

      encrypted_text = b'gAAAAABbA5d_aPZlueUfVlE9_a2e2NrW0Yk4epXb4zXvG-NDRmW_u7tcisN98RIgfWqJe39KF80UzwIn4UnsdsDjhfrIh2Y9OQ=='

      with open(key_file, 'rt') as key:
          #cipher_key = bytes.encode(key.read())
          cipher_key = key.read()

      decrypted_text = crypto_string(encrypted_text, cipher_key, 'decrypt')
      print(bytes.decode(decrypted_text))


main()

