#!/usr/bin/env python3

import os,time,tarfile
import logging
import io,socket
import configparser
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-v", "--verbose", action="store_true", 
                    help="Enable console output")
parser.add_argument("-c", "--configfile", action="store",dest="configfile", 
                    help="Specify configuration file")
parser.add_argument("-L", "--loglevel", action="store", dest="loglevel", choices="[debug, info, warn, error]",
                   help="Specify log level")

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

def sendToServer(HOST,LOCAL_FILE,REMOTE_FILE):
    import scp
    #client = scp.Client(host=HOST, user=backup, keyfile=keyfile)
    client = scp.Client(host=HOST, user=backup)
    client.use_system_keys()
    # Transfer file
    client.transfer(LOCAL_FILE, REMOTE_FILE)

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
            sources = config.get(section, 'sources').split(",")
            # Make paths absolute
            base_dir = os.path.expanduser('~') + os.sep + config.get(section, 'basedir')
            sources = [ os.path.expanduser('~') + os.sep + s for s in sources ]
            # Create base_dir if needed
            if os.path.exists(base_dir):
                base_msg = 'Using existing base directory: %s' % (base_dir)
            else:
                os.mkdir(base_dir)
                base_msg = 'Created base directory: %s' % (base_dir)

            # Logging stuff
            log_dir = base_dir + os.sep + 'logs'
            log_file = log_dir + os.sep + host_name + '_' + today + '-' + now + '.log'
            # Create log_dir if needed
            if os.path.exists(log_dir):
                log_msg = 'Using existing log directory: %s' % (log_dir)
            else:
                os.mkdir(log_dir)
                log_msg = 'Created log directory: %s' % (log_dir)

            # Set basic settings.
            archive_dir = base_dir + os.sep + 'archives' + os.sep + today
            archive_name = host_name + "_" + today + "-" + now + ".tar.gz"
            archive_path = archive_dir + os.sep + archive_name
            # Create archive directory if it isn't already there
            if os.path.exists(archive_dir):
                arc_msg = 'Using existing archive directory: %s' % (archive_dir)
            else:
                os.makedirs(archive_dir) # make directory
                arc_msg = 'Created archive directory: %s' % (archive_dir)

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
            remote_host = config.get(section, 'host')
            remote_path = config.get(section, 'path')
            logging.info('Remote Host:' + remote_host)
            logging.info('Remote Path:' + remote_path)
            # END remote section

        # Handle Mysql section.
        if 'mysql' in section:
            mysql_host = config.get(section, 'host') 
            mysql_port = config.get(section, 'port')
            logging.info('MySQL Host:' + mysql_host)
            logging.info('MySQL Port:' + mysql_port)
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

main()

