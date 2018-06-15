#!/usr/bin/env python3

import os,sys,socket,argparse,time
import hashlib,base64
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

# Set some global stuff
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


def hash_string(DATA):
    digest = hashlib.sha1(DATA.encode('utf-16-le')).digest()
    return base64.b64encode(digest)

def main():

    conx = pymysql.connect(read_default_file="~/.samy_io", db='crypto',
                           cursorclass=pymysql.cursors.DictCursor)

    if args.encrypt:
      cipher_key = Fernet.generate_key()

      # Write key to file
      try:
        open(key_file, 'wt').write(bytes.decode(cipher_key))

      except IOError:
        print ('Could not open key file: ' + key_file)
        print ('Bye!!!')
        sys.exit()


      # Read password from filesystem
      try:
        password = open(password_file, 'rt').read()

      except IOError:
        print ('Could not open password file: ' + password_file)
        print ('Bye!!!')
        sys.exit()

      string = str.encode(password)
      encrypted_text = bytes.decode(crypto_string(string, cipher_key, 'encrypt'))

      # Save encrypted string to DB
      try:
        with conx.cursor() as cursor:
          # Create a new record
          push_data = "UPDATE credentials SET Hostname=%s, Password=%s, DateStamp=%s WHERE user_id=%s"
          cursor.execute(push_data,(host_name, encrypted_text, now, 1))

        conx.commit()

      finally:
        conx.close()

      # Delete password file from filesystem
      try:
        os.remove(password_file)
      except OSError:
        pass


    if args.decrypt:

      with open(key_file, 'rt') as key:
          cipher_key = str.encode(key.read())

      # Get encrypted password from DB
      try:
        with conx.cursor() as cursor:
          # Read record
          pull_data = "SELECT Password FROM credentials WHERE user_id=%s"
          cursor.execute(pull_data,(1))
          encrypted_data = cursor.fetchone()

        conx.commit()

      finally:
        conx.close()

      encrypted_str = encrypted_data.get('Password')
      decrypted_text = crypto_string(str.encode(encrypted_str), cipher_key, 'decrypt')
      print(bytes.decode(decrypted_text))


    if args.init:

      # Create and initiailize database and table
      try:
        with conx.cursor() as cursor:
          #Create table and initialize data.
          create_table = "CREATE TABLE crypto.credentials (`user_id` int(11) NOT NULL AUTO_INCREMENT, `Hostname` varchar(100) NOT NULL,`Password` varchar(100) NOT NULL,`DateStamp` datetime NOT NULL, PRIMARY KEY (user_id)) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='User Credentials';"

          init_data = "INSERT INTO crypto.credentials (Hostname, Password, DateStamp) VALUES ( %s, 'nothing', %s);"

          cursor.execute(create_data)
          cursor.execute(init_data,(host_name, now))
          encrypted_data = cursor.fetchone()

        conx.commit()

      finally:
        conx.close()


main()

