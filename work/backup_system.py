#!/usr/bin/env python3

import os,time,tarfile,logging,io,socket,subprocess
import configparser,argparse,getpass
import paramiko
import smtplib

parser = argparse.ArgumentParser()
parser.add_argument("-v","--verbose",action="store_true",
                    help="Enable console output")
parser.add_argument("-c","--configfile",action="store",dest="configfile",
                    help="Specify configuration file")
#parser.add_argument("-L","--loglevel",action="store",dest="loglevel",choices="[debug,info,warn,error]",help="Specify log level")

args = parser.parse_args()

if args.verbose:
    print('Verbose Mode Set')

if args.configfile and os.path.exists(args.configfile):
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
    logging.info('Archive Complete.')


def directory_check(NAME, PATH):
    # Create directory if it isn't already there
    if os.path.exists(PATH):
        msg = 'Using existing %s directory: %s' % (NAME, PATH)
    else:
        os.makedirs(PATH) # make directory
        msg = 'Creating %s directory: %s' % (NAME, PATH)
    return msg


def scp_file(HOST,PORT,USER,KEY_FILE,LOCAL_FILE,REMOTE_FILE):
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


def mysql_bu(HOST, CREDS, SCHEMAS, LOCATION):
    try:
        timestamp = str(int(time.time()))

        schemas = ' '.join(SCHEMAS)

        if (schemas == 'all'):
            mydumpoptions = ' --routines --events --opt --all-databases ';
            p = subprocess.Popen("mysqldump --defaults-extra-file=" + CREDS + mydumpoptions + " > " + LOCATION + os.sep + "dump_" + HOST + "_" + timestamp + ".mysql", shell=True)

        else:
            mydumpoptions = ' --routines --events --opt --databases ';
            p = subprocess.Popen("mysqldump --defaults-extra-file=" + CREDS + mydumpoptions + schemas + " > " + LOCATION + os.sep + "dump_" + HOST + "_" + timestamp + ".mysql", shell=True)

        # Wait for completion
        p.communicate()
        # Check for errors
        if (p.returncode != 0):
            raise
        logging.info("MySQL dump completed for " + HOST)
    except:
        logging.info("MySQL dump failed for " + HOST)


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
            # Handle directory.
            base_msg = directory_check('base', base_dir)

            # Logging stuff
            log_dir = base_dir + os.sep + 'logs'
            log_file = log_dir + os.sep + host_name + '_' + today + '-' + now + '.log'
            # Handle directory.
            log_msg = directory_check('log', log_dir)

            # Set archive settings.
            archive_dir = base_dir + os.sep + 'archives' + os.sep + today
            archive_name = host_name + "_" + today + "-" + now + ".tar.gz"
            archive_path = archive_dir + os.sep + archive_name
            # Handle directory.
            arc_msg = directory_check('archive', archive_dir)

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

            logging.info('Remote User: ' + remote_user)
            logging.info('Remote Host: ' + remote_host)
            logging.info('Remote Port: ' + str(remote_port))
            logging.info('Remote Path: ' + remote_path)
            logging.info('Key File: ' + key_file)

            # END remote section

        # Handle MySQL section.
        if 'mysql' in section:
            mysql_host = config.get(section, 'host') 
            logging.info('MySQL Host: ' + mysql_host)
            
            mysql_base = config.get(section, 'base_dir')
            if not mysql_base.startswith('/'):
                mysql_base = os.path.expanduser('~') + os.sep + config.get(section, 'base_dir')
            
            mysql_msg = directory_check('mysql', mysql_base)
            logging.debug(mysql_msg)
            logging.info('MySQL Base Directory: ' + mysql_base)

            if config.has_option(section, 'defaults_extra_file'):
                mysql_defex = config.get(section, 'defaults_extra_file')
                
            if os.path.exists(mysql_defex):
                logging.info('MySQL Defaults Extra File: ' + mysql_defex)

            #else:
            #    if config.has_option(section, 'socket') and mysql_host == 'localhost':
            #        mysql_socket = config.get(section, 'socket')
            #        logging.info('MySQL Socket:' + mysql_socket)
            #    else:
            #        mysql_port = config.get(section, 'port')
            #        logging.info('MySQL Port:' + mysql_port)

            # Schema list to backup.
            
            mysql_schema_list = config.get(section, 'schemas').split(",")

            logging.info("Adding " + mysql_base + " to backup sources.")
            sources+=[mysql_base]

            mysql_bu(mysql_host, mysql_defex, mysql_schema_list, mysql_base)

            # END MySQL section

        # Handle Gerrit section.
        if 'gerrit' in section:
            # Location to backup.
            gerrit_base = config.get(section, 'base_dir')
            logging.info('Gerrit Base Directory: ' + gerrit_base)

            # END gerrit section

        # Handle Redis section.
        if 'redis' in section:
            # Location to backup.
            redis_base = config.get(section, 'base_dir')
            logging.info('Redis Base Directory: ' + redis_base)

            # END Redis section

        # Pretty much done with groking sections. l8!!!
        # Print some useful info to terminal. Useful for dev and debug.
        if args.verbose:
            print("Section ::: %s" % section)
            for options in config.options(section):
                print("Option | Value | Type ::: %s | %s | %s" % (options,config.get(section, options),str(type(options))))

    # END Handling sections.

    # These actions are last so we can include everything ready for processing.

    # Final check to make sure all the paths are absolute.
    source_paths = [os.path.abspath(path) for path in sources]
    # Create archive.
    create_archive(source_paths, archive_path)
    # Send archive file to remote system.
    #scp_file(remote_host,remote_port,remote_user,key_file,archive_path,remote_path)

main()

