#!/bin/bash
#
# This script will back up the gerrit environment.
# Included in the environment is /srv/gerrit
# and the MySQL database, reviewdb.
#

DATESTAMP=$(date +%FT%H%M%S)
HOSTNAME=$(hostname -s)

# Here's where Gerrit lives.
export GERRIT_HOME='/srv/gerrit'

# Here's where the archive file will be placed.
ARCHIVE_DIR='/mnt/backup'

# Set the ARCHIVE_FILE name.
ARCHIVE_FILE="${ARCHIVE_DIR}/${HOSTNAME}-gerrit.tar.gz"

# This is the destination and staging for the backup files.
BAKUP_DIR='/home/rudebwoy/backup'

# This is where all the log files will be deposited.
BAKUP_LOG=${BAKUP_DIR}/log

# This is the location used when dumping the MySQL schema for reviewdb.
BAKUP_SQL=${BAKUP_DIR}/mysql

# BACKUP_SERVER is the system where the packaged files will be copied for safe keeping.
BACKUP_SERVER="alb-ops-mon"

# BACKUP_SERVER_PATH is the full path where the packaged backup will be copied for safe keeping.
BACKUP_SERVER_PATH="/mnt/backups/${HOSTNAME}"

# set the log file
LOGFILE=${BAKUP_LOG}/backup-gerrit_${DATESTAMP}.log

help() {
    echo "Display Help"
    echo -e "Usage:\n"
    echo -e "$0 [ -h ] | [ -v ] | [ -d ] \n"
    echo -e "   Option         Description"
    echo -e "    -h              Display help / usage."
    echo -e "    -d              Debug Mode"
    echo
    exit
}

bakup() {
    if [ $1 == "db" ]; then
        # Set the command to back up the reviewdb schema in MySQL.
        CMD="mysqldump --defaults-extra-file=/root/.samy_su -l -F reviewdb --result-file=${BAKUP_SQL}/backup_reviewdb.sql"
    elif [ $1 == "gerrit" ]; then
        # Set the command to back up the gerrit file system.
        CMD="tar czf ${ARCHIVE_FILE} -C /srv gerrit -C ${BAKUP_DIR} mysql"
    else
        echo -e "Unknown option passed to function gerritinit()"
    fi
    makeitso
}

makeitso() {
    if [ $DEBUG ]; then
        echo -e "Command:  $CMD"
        return $?
    else
        echo -e "\nExecuting:  $CMD"
    fi
    $CMD
    unset CMD
}

#####################################################################
# Main
#####################################################################

# Redirect stdout (1) and stderr (2) to log file.
exec > ${LOGFILE} 2>&1

# Handle command line optionts.
if [ -z $1 ]; then
    # No option
    echo -e "No option specified"
    #help
elif [ $1 == "-d" ]; then
    # Set debug mode
    DEBUG=DEBUG
    echo "Debug Mode"
elif [ $1 == "-h" ]; then
    # Display help / usage
    help
fi

# Stop the server
CMD="systemctl stop gerrit"
makeitso

# Backup the DB
bakup db

# Backup the file system.  This also creates the archive file.
bakup gerrit

# Start the server
CMD="systemctl start gerrit"
makeitso

CMD="scp ${ARCHIVE_FILE} backup@${BACKUP_SERVER}:${BACKUP_SERVER_PATH}/"
makeitso

