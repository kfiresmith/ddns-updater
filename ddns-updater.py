#!/bin/env -B python3

import configparser
import os
import socket
import sys
import urllib.request

config = configparser.ConfigParser()
configfile = "ddns-updater.conf"

def load_config():
    # Verify config file exists
    conf_abs_path = "/etc/dnsdynamic-updater/{}".format(configfile)
    if os.path.exists(conf_abs_path) is False:
        print("{} file appears to be missing.".format(configfile))
        sys.exit(2)
    # Read config file
    os.chdir("/")
    config.read(os.path.join(os.path.abspath(os.path.dirname(__file__)),
                'etc', 'dnsdynamic-updater', configfile))

def load_fake_config():
    # Read config file
    config.read(configfile)

def read_config():
    # Parse variables from config file
    try:
        global provider
        provider= config['main']['provider']
        global dyn_account
        dyn_account = config[provider]['dyn_account']
        global dyn_passwd
        dyn_passwd = config[provider]['dyn_passwd']
        global dyn_hostname
        dyn_hostname = config[provider]['dyn_hostname']
    except NameError as ne:
        print(ne)
        print("The configuration file exists but appears to be missing a section")
        sys.exit(2)
    except KeyError as ke:
        print(ke)
        print("The configuration file exists but appears to be missing values")
        sys.exit(2)
    return dyn_account, dyn_passwd, dyn_hostname


def fresh_data(dyn_hostname):
    # Grab current DNS record
    try:
        current_record = socket.gethostbyname(dyn_hostname)
    except socket.gaierror as ge:
        print("Problem doing lookup of current hostname record for {}".format(dyn_hostname))
        print(ge)
        sys.exit(3)

    # Grab current IP
    ip_source = "https://api.ipify.org"
    myip = urllib.request.urlopen(ip_source).read().decode("utf-8")

    #Return results
    return current_record, myip

def google_dns_update(dyn_account, dyn_passwd, dyn_hostname, myip):
    update_string = ["https://{}:{}@domains.google.com/nic/update?hostname={}&myip={}"
                         .format(dyn_account, dyn_passwd, dyn_hostname, myip)]
    return update_string




load_fake_config()
read_config()


(current_record, myip) = fresh_data(dyn_hostname)
if (current_record != myip):
    print(google_dns_update(dyn_account, dyn_passwd, dyn_hostname, myip))

