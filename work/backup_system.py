#!/usr/bin/env python

import os,time,tarfile,logging
import io,socket
from ConfigParser import ConfigParser
#import scp
from paramiko import SSHClient
from scp import SCPClient
import smtplib

# System data
host_name = socket.gethostname()
now = time.strftime('%H%M%S')
today = time.strftime('%Y%m%d')
config_file = "backup_system.ini"

# Load the configuration file
try:
    config = ConfigParser()
    config.read(config_file)

except IOError:
    print "Could not read config file: " + config_file
    print "Bye!!!"
    sys.exit()

def create_archive(PATHS, ARCHIVE):
    logging.debug('Function: create_archive')
    logging.info('Creating archive file.')
    # Make sure all the paths are absolute.
    source_paths = [os.path.abspath(p) for p in PATHS]
    # Expand source paths to absolute for debug.
    for d in range(0, len(source_paths)):
        message = 'Source Path (absolute) %s:%s' % (d, source_paths[d])
        logging.debug(message)
 
    # Add sources to archive.
    try:
        with tarfile.open(ARCHIVE, "w:gz") as tf:
            logging.info('Archive File:' + ARCHIVE)
            for path in zip(source_paths):
                path = ''.join(path)
                logging.debug ('Source Path: ' + path)
                arc_path = path.replace('/', '-').replace('-', '', 1)
                logging.debug('In-Archive Path: ' + arc_path)
                tf.add(path, arcname=arc_path)
        xit = 'Successful'

     except IOError:
         xit = 'Problems creating archive'
         logging.info(xit)

    # Return status
    return xit

def send_to_server(REMOTE_HOST,LOCAL_FILE,REMOTE_FILE):
    logging.debug('Function: send_to_server')

    ssh = SSHClient()
    ssh.load_system_host_keys()
    ssh.connect(REMOTE_HOST)

    with SCPClient(ssh.get_transport()) as scp:
        scp.put(LOCAL_FILE, REMOTE_FILE)

    return xit

def send_email(FROM,TO,SUBJECT,TEXT,ATTACHMENT):
    logging.debug('Function: send_email')

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
    # Handle the sections.
    for section in config.sections():
        # Known sections.
        if 'default' in section:
            # Set default settings
            sources = config.get(section, 'sources').split(",")
            base_dir = config.get(section, 'base_dir')

            # Logging stuff
            logdir = base_dir + os.sep + 'logs'
            logfile = logdir + os.sep + host_name + '_' + today + '-' + now + '.log'
            # Create Logfile dir if needed
            if not os.path.exists(logdir):
                os.mkdir(logdir)

            # Set basic settings.
            target_dir = base_dir + os.sep + today
            target_name = host_name + "_" + today + "-" + now + ".tar.gz"
            target_path = target_dir + os.sep + target_name

            # Open logfile and set level
            logging.basicConfig(filename=logfile,level=logging.DEBUG)

            # Print some info
            logging.info('Logfile: ' + logfile)
            logging.info('Hostname: ' + host_name)
            logging.info('Date Stamp: ' + today + '-' + now)
            logging.info('Config File: ' + config_file)
            logging.info('Destination:' + base_dir)
            # Expand source directories.
            for d in range(0, len(sources)):
                message = 'Source Directory %s:%s' % (d, sources[d])
                logging.info(message)

            # Create archive directory if it isn't already there
            if not os.path.exists(target_dir):
                os.mkdir(target_dir) # make directory
                logging.info('Created archive directory: ' + target_dir)
            # END default section

        # Handle remote section.
        if 'remote' in section:
            remote_host = config.get(section, 'host')
            remote_user = config.get(section, 'user')
            remote_path = config.get(section, 'path')
            logging.info('Remote Host:' + remote_host)
            logging.info('Remote User:' + remote_user)
            logging.info('Remote Path:' + remote_path)
            # END remote section

        # Handle Mysql section.
        if 'mysql' in section:
            mysql_host = config.get(section, 'host') 
            mysql_user = config.get(section, 'user') 
            mysql_port = config.get(section, 'port')
            mysql_databases = config.get(section, 'databases').split(",")
            logging.info('MySQL Host:' + mysql_host)
            logging.info('MySQL Port:' + mysql_port)
            # Expand databases.
            for d in range(0, len(mysql_databases)):
                message = 'Database Schema %s:%s' % (d, mysql_databases[d])
                logging.info(message)
            # END mysql section

        # Pretty much done with groking sections.

    # END Handling sections.

    # Do work!!!

    # This stuff is last so we can include everything ready for processing.
    archive_status=create_archive(sources, target_path)
    logging.info('Status [create_archive]: ' + archive_status)

main()
