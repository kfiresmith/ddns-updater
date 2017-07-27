#!/bin/env -B python3

import configparser
import os
import re
import requests
import socket
import sys
import syslog
import time


progname = 'ddns-updater'
configfile = "ddns-updater.conf"
config = configparser.ConfigParser()

# This will eventually be done via a command switch...
verbose = True


if verbose:
    syslog.syslog("Starting up")
    print("Starting up {}".format(progname))


def read_config():
    # Verify config file exists
    conf_abs_path = "/etc/ddns-updater/{}".format(configfile)
    if os.path.exists(conf_abs_path) is False:
        print("{} file appears to be missing.".format(configfile))
        syslog.syslog("Fatal: Configuration file not found! Exiting")
        sys.exit(2)
    # Read config file
    os.chdir("/")
    config.read(os.path.join(os.path.abspath(os.path.dirname(__file__)),
                'etc', 'ddns-updater', configfile))


def read_fake_config():
    # Read a non-git config for in-place testing w/ creds
    configfile = "ddns-updater-local.conf"
    config.read(configfile)


def parse_config():
    # Parse variables from config file
    global provider
    global dyn_account
    global dyn_hostname
    global dyn_passwd
    syslog.syslog("reading {}".format(configfile))
    if verbose:
        print("reading {}".format(configfile))
    try:
        provider = config['main']['provider']
        dyn_account = config[provider]['dyn_account']
        dyn_passwd = config[provider]['dyn_passwd']
        dyn_hostname = config[provider]['dyn_hostname']
    except NameError as ne:
        errmsg = "Fatal: The configuration file exists but appears to be missing a section"
        print("{}: {}".format(errmsg, ne))
        syslog.syslog("{}: {}".format(errmsg, ne))
        sys.exit(2)
    except KeyError as ke:
        errmsg = "Fatal: The configuration file exists but appears to be missing values"
        print("{}: {}".format(errmsg, ke))
        syslog.syslog("{}: {}".format(errmsg, ke))
        sys.exit(2)
    return dyn_account, dyn_passwd, dyn_hostname


def is_valid_hostname(hostname):
    # https://stackoverflow.com/questions/2532053/validate-a-hostname-string/2532344#2532344
    # Credit: Tim Pietzcker (Thanks for doing the regex so I don't have to)
    if len(hostname) > 255:
        return False
    if hostname[-1] == ".":
        hostname = hostname[:-1] # strip exactly one dot from the right, if present
    allowed = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
    return all(allowed.match(x) for x in hostname.split("."))


def fresh_data(dyn_hostname):
    # Grab current DNS record
    try:
        current_record = socket.gethostbyname(dyn_hostname)
    except socket.gaierror as ge:
        errmsg = "Problem doing lookup of current hostname record for {}".format(dyn_hostname)
        print("{}: {}".format(errmsg, ge))
        syslog.syslog("{}: {}".format(errmsg, ge))
        sys.exit(3)
    # Grab current IP
    ip_source = "https://api.ipify.org"
    myip = requests.get(ip_source).text
    return current_record, myip


def google_dns_update(dyn_account, dyn_passwd, dyn_hostname, myip):
    update_string = "https://{}:{}@domains.google.com/nic/update?hostname={}&myip={}" \
                         .format(dyn_account, dyn_passwd, dyn_hostname, myip)
    return update_string


read_fake_config()
parse_config()
while is_valid_hostname(dyn_hostname):
    try:
        (current_record, myip) = fresh_data(dyn_hostname)
        if (current_record != myip):
            if provider == 'google':
                update_job = requests.get(google_dns_update(dyn_account, dyn_passwd, dyn_hostname, myip))
                type(update_job)
                print(update_job)
                # TODO: use response for $logic and logging
                # put logging in place
        time.sleep(5)
    except KeyboardInterrupt as ki:
        syslog.syslog("termination requested; shutting down")
        print("termination requested; shutting down")
        sys.exit(0)


