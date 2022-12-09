#!/usr/bin/env python3

import os,time,logging
import io,socket
#from configparser import ConfigParser

# System data
host_name = socket.gethostname()
now = time.strftime('%H%M%S')
today = time.strftime('%Y%m%d')
config_file = "ping-test.ini"

# Load the configuration file
try:
    config = ConfigParser()
    config.read(config_file)

except IOError:
    print("Could not read config file: " + config_file)
    print("Bye!!!")
    sys.exit()

def main():
    

main()
