#!/usr/bin/env python3

import os,argparse
import pymysql
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

    #conn = pymysql.connect(host='127.0.0.1', unix_socket='/tmp/mysql.sock', user='root', passwd=None, db='mysql')
    #cur = conn.cursor()

    if args.encrypt:
      password = 'Whut3v4Mang!'
      string = str.encode(password)
      cipher_key = Fernet.generate_key()
      key_file = os.path.expanduser('~') + os.sep + '.iok'

      try:
        open(key_file, 'wt').write(bytes.decode(cipher_key))

      except IOError:
        print ('Could not open key file: ' + key_file)
        print ('Bye!!!')
        sys.exit()

      encrypted_text = crypto_string(string, cipher_key, 'encrypt')
      print(encrypted_text)

      #cur.execute("SELECT * FROM user")
      #for r in cur:
      #    print(r)

      data = (encrypted_text, now.strftime('%Y-%m-%d'), now.strftime('%H:%M:%S'))

    if args.decrypt:
      key_file = os.path.expanduser('~') + os.sep + '.iok'

      encrypted_text =  'gAAAAABbBI9Ca0ADXQ6FZQb1D9UwDx6XVdJFzjsIH2-06oUJnZspD2Y7TRAwMPoCH6CbrfeyznNVXzJ8pCgAxxwbPoFc9x7ACQ=='

      with open(key_file, 'rt') as key:
          cipher_key = str.encode(key.read())
          #cipher_key = key.read()

      decrypted_text = crypto_string(str.encode(encrypted_text), cipher_key, 'decrypt')
      print(bytes.decode(decrypted_text))

    #cur.close()
    #conn.close()


main()

