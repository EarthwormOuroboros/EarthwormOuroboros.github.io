#!/usr/bin/env python3

import os,sys,socket,argparse
import time
import pymysql
from cryptography.fernet import Fernet
from datetime import date, datetime, timedelta

parser = argparse.ArgumentParser()
parser.add_argument("-d","--decrypt",action="store_true",
                    help="Fetch data")
parser.add_argument("-e","--encrypt",action="store_true",
                    help="Set data.")
parser.add_argument("-i","--init",action="store_true",
                    help="Install data.")

args = parser.parse_args()

host_name = socket.gethostname()
now = time.strftime('%Y-%m-%d %H:%M:%S')
key_file = os.path.expanduser('~') + os.sep + '.iok'
password_file = os.path.expanduser('~') + os.sep + '.iok_secret'


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

    conx = pymysql.connect(host='192.168.232.9', user='lorenzo', passwd='Fuxm3Running!', db='crypto')
    cur = conx.cursor()

    if args.encrypt:
      cipher_key = Fernet.generate_key()

      try:
        open(key_file, 'wt').write(bytes.decode(cipher_key))

      except IOError:
        print ('Could not open key file: ' + key_file)
        print ('Bye!!!')
        sys.exit()


      try:
        password = open(password_file, 'rt').read()

      except IOError:
        print ('Could not open key file: ' + password_file)
        print ('Bye!!!')
        sys.exit()

      string = str.encode(password)
      encrypted_text = crypto_string(string, cipher_key, 'encrypt')
      print(encrypted_text)

      push_data = ("""UPDATE credentials SET Hostname=%s Password=%s DateStamp=%s WHERE id=%s""", 
                   (host_name, encrypted_text, now, '1'))

      push_data = ("""INSERT INTO credentials (Hostname, Password, DateStamp) VALUES (%s, %s, %s)""",
                   (host_name, encrypted_text, now))

      cur.execute(push_data)


      try:
        os.remove(filename)
      except OSError:
        pass

    if args.decrypt:
      encrypted_text =  'gAAAAABbBI9Ca0ADXQ6FZQb1D9UwDx6XVdJFzjsIH2-06oUJnZspD2Y7TRAwMPoCH6CbrfeyznNVXzJ8pCgAxxwbPoFc9x7ACQ=='

      with open(key_file, 'rt') as key:
          cipher_key = str.encode(key.read())
          #cipher_key = key.read()

      decrypted_text = crypto_string(str.encode(encrypted_text), cipher_key, 'decrypt')
      print(bytes.decode(decrypted_text))

    #cur.close()
    #conn.close()


main()

