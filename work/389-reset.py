#!/usr/bin/env python2

import os,sys,socket,argparse,time
import MySQLdb
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


def main():

    db = MySQLdb.connect(read_default_file="~/.samy_io", db='crypto')
    cur = db.cursor()

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
        # Create a new record
        push_data = "UPDATE credentials SET Hostname='%s', Password='%s', DateStamp='%s' WHERE user_id=%s;" % (host_name, encrypted_text, now, 1)
        cur.execute(push_data)
        db.commit()

      finally:
        cur.close()
        db.close()

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
        # Read record
        pull_data = "SELECT Password FROM credentials WHERE user_id=1;"
        cur.execute(pull_data)
        encrypted_data = cur.fetchone()
        db.commit()

      finally:
        cur.close()
        db.close()

      encrypted_str = str(encrypted_data)
      decrypted_text = crypto_string(str.encode(encrypted_str), cipher_key, 'decrypt')
      print(bytes.decode(decrypted_text))


    if args.init:

      # Create and initiailize database and table to verify DB perms are correct.
      try:
        #Create table.
        create_table = "CREATE TABLE crypto.credentials (`user_id` int(11) NOT NULL AUTO_INCREMENT, `Hostname` varchar(100) NOT NULL,`Password` varchar(200) NOT NULL,`DateStamp` datetime NOT NULL, PRIMARY KEY (user_id)) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='User Credentials';"
        cur.execute(create_table)

        # Initialize data
        init_data = "INSERT INTO crypto.credentials (Hostname, Password, DateStamp) VALUES ( '%s', 'nothing', '%s');" % (host_name, now)
        cur.execute(init_data)
        db.commit()

      except MySQLdb.Error as err:
        print(err)

      finally:
        cur.close()
        db.close()


main()

