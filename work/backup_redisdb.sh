#!/bin/bash
#########################################################################
# backup_redis.sh
#
# Purpose: Back up Redis DB and configs.
#
# Created Date: 2016/10/03
# Created By: Lorenzo Wacondo, TEKsystems
#
#########################################################################
VERSION=0.9.0-20151022
ME=${0}

# set a few items
HOSTNAME=$(hostname -s)
DATESTAMP=$(date +%FT%H%M%S%z)

# Set backup path.
BAKUP_DPATH="/root/backup"

# DB location
REDISDB=/var/lib/redis

#
REDISCONF=/etc/redis

BACKUP_SERVER=alb-ops-mon
BACKUP_PATH="/mnt/backups/${HOSTNAME}"

# The recipient of the status email.
EMAIL_ADDRESS="lorenzo.wacondo@state.nm.us"

# Pull the trigger...
makeitso() {
    echo -e "** Command:"
    echo -e "**     ${CMD}"
    if ( eval ${CMD} )
    then
      echo -e "** Success!"
    else
      echo -e "** Failed!"
    fi
    unset CMD
}

help() {
    echo -e "Usage: ${ME} [ -h ]\n"
    echo -e "    -h   Display help."
    exit
}

# Check if any options were passed.
if [ "$1" == "-h" ]; then
    # Display help / usage
    help
    exit
fi

# Set archive and log file destinations.
LOGFILEDIR="${BAKUP_DPATH}/log"
if [ ! -e "${LOGFILEDIR}" ] ; then
  echo -e "** Directory not found: ${LOGFILEDIR}"
  CMD="mkdir -p ${LOGFILEDIR}"
  makeitso
fi

# Set log file.
LOGFILE="${LOGFILEDIR}/backup_redisdb_${DATESTAMP}.log"
# Redirect stdout (1) and stderr (2) to log file.
exec >${LOGFILE} 2>&1

bakup () {
    echo -e "\n** Hostname: ${HOSTNAME}"

    # Set the environment for the databases to export.
    #if [ "$1" == "facts" ] || [ "$1" == "" ] || [ "$1" == "" ] ; then
    if [ "$1" == "facts" ] ; then
        INSTANCE=${1}
        echo -e "** Instance: ${INSTANCE}"
    else
        echo -e "** Unknown option passed to bakup()"
        echo -e "**   Option: $1"
        echo -e "** Exiting..."
        exit
    fi

    # Create checksum file
    echo -e "\n** Creating SHA256 checksum for database file."
    CMD="sha256sum ${REDISDB}/${INSTANCE}/dump.rdb > ${REDISDB}/${INSTANCE}/dump.sha256sum"
    makeitso

    # set archive filename
    ARCFILE="${HOSTNAME}_${INSTANCE}_${DATESTAMP}.tar.xz"
    FILE_BASE_NAME="${HOSTNAME}_${INSTANCE}"

    # Set command line and create archive
    CMD="tar vcJpf $BAKUP_DPATH/$ARCFILE "
    CMD="$CMD -C ${REDISDB}/${INSTANCE} appendonly.aof dump.rdb dump.sha256sum"
    CMD="$CMD -C ${REDISCONF} ${INSTANCE}.conf "
    CMD="$CMD -C /root/bin backup_redisdb.sh"
    echo -e "\n** Creating archive."
    makeitso

    # Copy backup package to alb-ops-mon.
    echo -e "\n** Archive File:"
    ls -l ${BAKUP_DPATH}/${ARCFILE}
    echo -en "\n** Copying archive file to ${BACKUP_SERVER}"
    CMD="scp ${BAKUP_DPATH}/${ARCFILE} backup@${BACKUP_SERVER}:${BACKUP_PATH}/"
    if (eval ${CMD})
    then
      echo -e " complete!"
      # Begin cleanup of older archives.
      # Check if the place keeper file containing old file name is present.
      if [ -f ${BAKUP_DPATH}/.${FILE_BASE_NAME} ]
      then
        ARCFILE_OLD=$(cat ${BAKUP_DPATH}/.${FILE_BASE_NAME})
        CMD="ssh backup@${BACKUP_SERVER} ls -la ${BACKUP_PATH}/${ARCFILE}"
        if (eval ${CMD})
        then
          # Remove old remote archive.
          echo -en "\n** Removing old archive file from remote file system"
          CMD="ssh backup@${BACKUP_SERVER} rm -f ${BACKUP_PATH}/${ARCFILE_OLD}"
          if (eval ${CMD})
          then
            echo -e " complete."
          else
            echo -e " failed."
            echo -e "\n*** ERROR: deleting ${ARCFILE_OLD} on remote file system."
            echo -e "*** Server:  ${BACKUP_SERVER}"
            echo -e "*** Path:    ${BACKUP_PATH}/${ARCFILE_OLD}"
            echo -e "*** Remove file manually."
          fi
          # Remove old local archive
          echo -en "\n** Removing old archive file from local file system"
          CMD="rm -f ${BAKUP_DPATH}/${ARCFILE_OLD} "
          if (eval ${CMD})
          then
            echo -e " complete."
          else
            echo -e " failed."
            echo -e "\n*** ERROR: deleting ${ARCFILE_OLD} on local file system."
            echo -e "*** Path:    ${BAKUP_DPATH}/${ARCFILE_OLD}"
            echo -e "*** Remove file manually."
          fi
        else
          echo -e "\n*** ERROR: while looking for ${ARCFILE_OLD} on remote file system."
        fi
      # Done removing old file.
      fi
      # Save the new archive file name for later use.
      echo "${ARCFILE}" > ${BAKUP_DPATH}/.${FILE_BASE_NAME}
    else
      echo -e " failed."
      echo -e "\n*** ERROR: while copying archive file to the backup sever."
      echo -e "***  See ${ERRLOG} for details"
    fi

}

bakup facts

#  Clean up the log files.
#  Keep the latest 5 local copies.
echo -e "\n** Pruning log files, keeping last 5."
COUNT_LIMIT=5
for FILE in log err
do
  COUNT_CMD=$(echo -e "ls -lt ${LOGFILEDIR}/backup_redisdb_*.${FILE} | awk '{print \$9}' | wc -l")
  echo -e "\n** Command: ${COUNT_CMD}"
  COUNT=$(eval ${COUNT_CMD})
  echo -e "** Files Found: ${COUNT}"

  if [ ${COUNT} -gt 5 ] ; then
    # more than 5 files, need to delete
    echo -e "\n** Get list of files to delete."
    GETLIST_CMD=$(echo -e "ls -lt ${LOGFILEDIR}/backup_redisdb_*.${FILE} | awk '{print \$9}' | tail -n\$(( ${COUNT} - ${COUNT_LIMIT} ))")
    echo -e "** Command: ${GETLIST_CMD}"
    ERASE_LIST="$(eval ${GETLIST_CMD})"
    echo -e "\n** Files to remove,"
    echo -e "${ERASE_LIST}"
    # Verify we have a list
    if [ -z "${ERASE_LIST}" ]; then
      echo -e "** We have an empty list."
      echo -e "** Exiting..."
      exit
    fi
    # list the directories that need to be deleted
    CMD="rm -f ${ERASE_LIST}"
    makeitso
  fi
done

# Mail the logs to someone.
mailx -s "Backup status for ${HOSTNAME}" ${EMAIL_ADDRESS} < ${LOGFILE}

exit
