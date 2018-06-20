#!/usr/bin/env python2

import os,sys,socket,argparse,time,getpass
import hashlib,base64
import MySQLdb
from datetime import date, datetime, timedelta
import warnings
with warnings.catch_warnings():
    warnings.filterwarnings("ignore",category=DeprecationWarning)
    from cryptography.fernet import Fernet

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
user_name = getpass.getuser()
now = time.strftime('%Y-%m-%d %H:%M:%S')
key_file = '/usr/local/share/389ds/.iok'
hash_file = os.path.expanduser('~') + os.sep + '389-refresh' + os.sep + '.389sec'
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
    digest = hashlib.sha1(DATA.encode('utf-8')).digest()
    return base64.b64encode(digest)


def main():

    db = MySQLdb.connect(read_default_file="~/.samy_io", db='crypto')
    cur = db.cursor()

    if args.encrypt and user_name == 'ds389':
      # Read password from filesystem
      try:
        password = open(password_file, 'rt').read()

      except IOError:
        print ('Could not open password file: ' + password_file)
        print ('Bye!!!')
        sys.exit()

      # Generate new key
      cipher_key = Fernet.generate_key()

      # Write key to file
      try:
        open(key_file, 'wt').write(bytes.decode(cipher_key))

      except IOError:
        print ('Could not open key file: ' + key_file)
        print ('Bye!!!')
        sys.exit()

      hash = '{SHA}' + hash_string(password)

      # Write hash to file
      try:
        open(hash_file, 'wt').write(hash)

      except IOError:
        print ('Could not open hash file: ' + hash_file)
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


    if args.init and user_name == 'ds389':

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

