#!/bin/bash
###############################################################################
# Create a new redis instance.
###############################################################################

###############################################################################
# Handle the command line arguments.
###############################################################################

while getopts ":a:i:p:v" opt; do
    case $opt in
        a)  IP_ADDR=${OPTARG}
        ;;
        i)  INSTANCE_NAME=${OPTARG}
        ;;
        p)  IP_PORT=${OPTARG}
        ;;
        v)  VERBOSE=verbose
        ;;
    esac
done
shift $((${OPTIND} - 1))

###############################################################################
##  Main
###############################################################################

REDIS_ETC=/etc/redis

if [ ${VERBOSE} ]
then
    echo -e "Instance name : ${INSTANCE_NAME}"
    echo -e "IP Address : ${IP_ADDR}"
    echo -e "IP Port : ${IP_PORT}"
fi

if [ ! -z "${INSTANCE_NAME}" ]
then
    CONFIG_FILE="${REDIS_ETC}/${INSTANCE_NAME}.conf"

    echo "Creating new config file: ${CONFIG_FILE}"
    cp -a ${REDIS_ETC}/default.conf.example ${CONFIG_FILE}.conf

    echo -e "\nChanging config parameters for new instance."
    sed -i "s|^pidfile\ .*|pidfile /var/run/redis/${INSTANCE_NAME}.pid|g ; \
            s|^logfile\ .*|logfile /var/log/redis/${INSTANCE_NAME}.log|g ; \
            s|^dir\ .*|dir /var/lib/redis/${INSTANCE_NAME}/|g" \
            ${CONFIG_FILE}.conf

    echo -e "Lines altered:"
    grep -n -E '^pidfile|^logfile|^dir' ${CONFIG_FILE}.conf

    echo -e "\nCreating data directory: /var/lib/redis/${INSTANCE_NAME}/"
    install -d -o redis -g redis -m 0750 /var/lib/redis/${INSTANCE_NAME}/

    echo -e "\nCreating systemd service config directory: "
    echo -e "    /etc/systemd/system/redis@${INSTANCE_NAME}.service.d"
    install -d -m 0755 /etc/systemd/system/redis@${INSTANCE_NAME}.service.d

    echo -e "\nCreating systemd service config file: "
    echo -e "    /etc/systemd/system/redis@${INSTANCE_NAME}.service.d/limits.conf"
    echo -e "[Service]
LimitNOFILE=10240" > /etc/systemd/system/redis@${INSTANCE_NAME}.service.d/limits.conf

    echo -e "\nContents of systemd config file:"
    cat /etc/systemd/system/redis@${INSTANCE_NAME}.service.d/limits.conf
else
    echo -e "No instance name provided.  Nothing to do."
    exit
fi

if [ ! -z "${IP_ADDR}" ]
then
    echo -e "\nChanging config parameters for supplied IP Address."
    sed -i "s|^bind\ .*|bind ${IP_ADDR}|g" ${CONFIG_FILE}.conf

    echo -e "Lines altered:"
    grep -n '^bind' ${CONFIG_FILE}.conf
fi

if [ ! -z "${IP_PORT}" ]
then
    echo -e "\nChanging config parameters for supplied IP Port."
    sed -i "s|^port\ .*|port ${IP_PORT}|g" ${CONFIG_FILE}.conf

    echo -e "Lines altered:"
    grep -n '^port' ${CONFIG_FILE}.conf
fi
