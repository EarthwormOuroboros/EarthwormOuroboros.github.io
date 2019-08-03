#!/bin/bash
###############################################################################
# Create a new redis instance.
###############################################################################

REDIS_ETC=/etc/redis

if [ ! -z "${1}" ]
then

  INSTANCE_NAME=${1}

  cp -a ${REDIS_ETC}/default.conf.example ${REDIS_ETC}/${INSTANCE_NAME}.conf

  install -d -o redis -g redis -m 0750 /var/lib/redis/${INSTANCE_NAME}/

  install -d -m 0755 /etc/systemd/system/redis@${INSTANCE_NAME}.service.d

  echo "[Service]
LimitNOFILE=10240" > /etc/systemd/system/redis@${INSTANCE_NAME}.service.d/limits.conf

  cat /etc/systemd/system/redis@${INSTANCE_NAME}.service.d/limits.conf

  sed "s|^bind\ .*|bind ${IP_ADDR}|g" ${REDIS_ETC}/${INSTANCE_NAME}.conf

  sed "s|^port\ .*|port ${IP_PORT}|g" ${REDIS_ETC}/${INSTANCE_NAME}.conf

  sed "s|^pidfile\ .*|pidfile /var/run/redis/${INSTANCE_NAME}.pid|g ; s|^logfile\ .*|logfile /var/log/redis/${INSTANCE_NAME}.log|g ; s|^dir\ .*|dir /var/lib/redis/${INSTANCE_NAME}/|g" ${REDIS_ETC}/${INSTANCE_NAME}.conf

else
  echo -e "No instance name provided.  Nothing to do."
fi
