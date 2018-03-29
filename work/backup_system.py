#!/usr/bin/env python3

import os,time,tarfile
import logging
import io,socket
import configparser
import argparse
import getpass

parser = argparse.ArgumentParser()
parser.add_argument("-v","--verbose",action="store_true",
                    help="Enable console output")
parser.add_argument("-c","--configfile",action="store",dest="configfile",
                    help="Specify configuration file")
#parser.add_argument("-L","--loglevel",action="store",dest="loglevel",choices="[debug,info,warn,error]",help="Specify log level")

args = parser.parse_args()

if args.verbose:
    print('Verbose Mode Set')

if args.configfile:
    if os.path.exists(args.configfile):
        config_file = args.configfile
        conf_msg = 'Using specified config file: ' + config_file
else:
    config_file = "backup_system.ini"
    conf_msg = 'Using default config file: ' + config_file

try:
    with open(config_file) as f:
        config = configparser.RawConfigParser(allow_no_value=True)
        config.read_file(f)

except IOError:
    print ('Could not read config file: ' + config_file)
    print ('Bye!!!')
    sys.exit()


def create_archive(PATHS, ARCHIVE):
    with tarfile.open(ARCHIVE, "w:gz") as tf:
        logging.info('Archive File:' + ARCHIVE)
        for path in zip(PATHS):
            path = ''.join(path)
            logging.info ('Adding Source Path: ' + path)
            arc_path = path.replace('/', '-').replace('-', '', 1)
            logging.info('In-Archive Path: ' + arc_path)
            tf.add(path, arcname=arc_path)

def sendToServer(HOST,PORT,USER,KEY_FILE,LOCAL_FILE,REMOTE_FILE):
    import paramiko

    # Transfer file
    try:
        key = paramiko.RSAKey.from_private_key_file(KEY_FILE)
        t = paramiko.Transport((HOST, PORT))
        t.connect( username = USER, pkey = key)
        sftp = paramiko.SFTPClient.from_transport(t)
        sftp.put(LOCAL_FILE, REMOTE_FILE)

    finally:
        t.close()

def sendMail(FROM,TO,SUBJECT,TEXT,ATTACHMENT):
    import smtplib

    # Email message
    message = """\
        From: %s
        To: %s
        Subject: %s
        %s
        """ % (FROM, ", ".join(TO), SUBJECT, TEXT)

    # Send the message
    server = smtplib.SMTP('localhost')
    server.sendmail(FROM, TO, message)
    server.quit()

def main():
    # System data
    host_name = socket.gethostname()
    now = time.strftime('%H%M%S')
    today = time.strftime('%Y%m%d')

    # Handle the sections.
    for section in config.sections():
        # Known sections.
        if 'default' in section:
            # Default stuff

            # Base dir relative to home dir unless absolute
            base_dir = config.get(section, 'basedir')
            if not base_dir.startswith('/'):
              base_dir = os.path.expanduser('~') + os.sep + config.get(section, 'basedir')

            # Sources not absolute are relative to the home dir of the user running the script.
            sources = [ os.path.expanduser('~') + os.sep + s if not s.startswith('/') else s for s in config.get(section, 'sources').split(",") ]

            # Create base_dir if needed
            if os.path.exists(base_dir):
                base_msg = 'Using existing base directory: %s' % (base_dir)
            else:
                base_msg = 'Creating base directory: %s' % (base_dir)
                os.mkdir(base_dir)

            # Logging stuff
            log_dir = base_dir + os.sep + 'logs'
            log_file = log_dir + os.sep + host_name + '_' + today + '-' + now + '.log'
            # Create log_dir if needed
            if os.path.exists(log_dir):
                log_msg = 'Using existing log directory: %s' % (log_dir)
            else:
                log_msg = 'Creating log directory: %s' % (log_dir)
                os.mkdir(log_dir)

            # Set archive settings.
            archive_dir = base_dir + os.sep + 'archives' + os.sep + today
            archive_name = host_name + "_" + today + "-" + now + ".tar.gz"
            archive_path = archive_dir + os.sep + archive_name
            # Create archive directory if it isn't already there
            if os.path.exists(archive_dir):
                arc_msg = 'Using existing archive directory: %s' % (archive_dir)
            else:
                os.makedirs(archive_dir) # make directory
                arc_msg = 'Creating archive directory: %s' % (archive_dir)

            # Open logfile and set level
            logging.basicConfig(filename=log_file,level=logging.DEBUG,format='%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%dT%H:%M:%S')

            # Output some info
            logging.info('Logfile: ' + log_file)
            logging.info('Hostname: ' + host_name)
            logging.debug('Date Stamp: ' + today + '-' + now)
            logging.info(conf_msg)
            logging.debug(base_msg)
            logging.debug(log_msg)
            logging.debug(arc_msg)

            # Print source directories
            for d in range(0, len(sources)):
                message = 'Source Directory %s:%s' % (d, sources[d])
                logging.debug(message)

            # END default section

        # Handle remote section.
        if 'remote' in section:
            if config.has_option(section, 'user'):
                remote_user = config.get(section, 'user')
            else:
                remote_user = getpass.getuser()

            if config.has_option(section, 'port'):
                remote_port = config.get(section, 'port')
            else:
                remote_port = 22

            if config.has_option(section, 'keyfile'):
                key_file = config.get(section, 'keyfile')
            else:
                key_file = os.path.expanduser('~') + os.sep + '.ssh/id_rsa'

            remote_host = config.get(section, 'host')
            remote_path = config.get(section, 'path') + os.sep + archive_name

            logging.info('Remote User:' + remote_user)
            logging.info('Remote Host:' + remote_host)
            logging.info('Remote Port:' + str(remote_port))
            logging.info('Remote Path:' + remote_path)
            logging.info('Key File:' + key_file)
            # END remote section

        # Handle Mysql section.
        if 'mysql' in section:
            mysql_host = config.get(section, 'host') 
            logging.info('MySQL Host:' + mysql_host)

            if config.has_option(section, 'socket'):
                mysql_socket = config.get(section, 'socket')
                logging.info('MySQL Socket:' + mysql_socket)
            else:
                mysql_port = config.get(section, 'port')
                logging.info('MySQL Port:' + mysql_port)

            # Schema list to backup.
            mysql_schema_list = config.get(section, 'schemas').split(",")

            # END mysql section

        # Pretty much done with groking sections. l8!!!
        # Print some useful info to terminal. Useful for dev and debug.
        if args.verbose:
            print("Section ::: %s" % section)
            for options in config.options(section):
                print("Option | Value | Type ::: %s | %s | %s" % (options,config.get(section, options),str(type(options))))

    # END Handling sections.

    # This is last so we can include everything ready for processing.
    #
    # Make sure all the paths are absolute.
    source_paths = [os.path.abspath(path) for path in sources]
    # Create archive.
    create_archive(source_paths, archive_path)

    # Send archive file to remote system.
    sendToServer(remote_host,remote_port,remote_user,key_file,archive_path,remote_path)

main()

