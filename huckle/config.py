from __future__ import absolute_import, division, print_function

from configparser import ConfigParser
from io import StringIO
from os import listdir
from os.path import isfile, join
from os import path

# huckle's imports
from . import hutils

import os
import sys
import shutil
import json

root = os.path.abspath(os.path.dirname(__file__))
huckle_manpage_path = root + "/data/huckle.1"
home = os.path.expanduser("~")
dot_huckle = "%s/.huckle" % home
dot_huckle_scripts = dot_huckle + "/bin"
dot_huckle_config = dot_huckle + "/etc"
dot_bash_profile = home + "/.bash_profile"
dot_bashrc = home + "/.bashrc"

# These next 3 variables are dynamically updated from read configuration. Be careful!
url = ""
cliname = "huckle"
cli_manpage_path = "/tmp"
ssl_verify = "verify"
url_pinning = "dynamic"

# URL Pinning lookup
pinned_urls = {}

# These hcli_ variables are taken from the semantic types found in the HCLI 1.0 specification
hcli_command_type = "command"
hcli_option_type = "option"
hcli_parameter_type = "parameter"
hcli_execution_type = "execution"

# parses the configuration of a given cli to set configured execution
def parse_configuration(cli):
    config_file_path = dot_huckle_config + "/" + cli + "/config"
    parser = ConfigParser()
    parser.read(config_file_path)
    if parser.has_section("default"):
        for section_name in parser.sections():
            for name, value in parser.items("default"):
                if name == "url":
                    global url
                    url = value
                    global cliname
                    cliname = cli
                    global cli_manpage_path
                    cli_manpage_path = cli_manpage_path + "/huckle." + cliname
                if name == "ssl.verify":
                    global ssl_verify
                    ssl_verify = value
                if name == "url.pinning":
                    global url_pinning
                    url_pinning = value
            if url == "": sys.exit("No url defined for " + cli + " under " + config_file_path)
    else:
        sys.exit("huckle: no cli configuration " + config_file_path + " available for " + cli) 

    pinned_file_path = dot_huckle_config + "/" + cli + "/pinned.json"
    try:
        with open(pinned_file_path, 'r') as file:
            global pinned_urls
            pinned_urls = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        pinned_urls = {}

def pin_url(command, url, method):
    if command not in pinned_urls:
        pinned_urls[command] = {}
    pinned_urls[command]["url"] = url
    pinned_urls[command]["method"] = method
    save_pinned_urls()

# return a url and method if there's a cache hit.
def get_pinned_url(command):
    if command in pinned_urls:
        return pinned_urls[command]["url"], pinned_urls[command]["method"]
    else:
        return None, None

def save_pinned_urls():
    pinned_file_path = dot_huckle_config + "/" + cliname + "/pinned.json"
    with open(pinned_file_path, 'w') as file:
        json.dump(pinned_urls, file)

# creates a configuration file for a named cli
def create_configuration(cli, url):
    config_file_folder = dot_huckle_config + "/" + cli
    config_file = config_file_folder + "/config"
    hutils.create_folder(config_file_folder)

    if not os.path.exists(config_file):
        hutils.create_file(config_file)
        init_configuration(cli, url)
    else:
        text = "huckle: the configuration for " + cli + " already exists. leaving the existing configuration untouched."
        return text

    hutils.create_folder(cli_manpage_path + "/huckle." + cli)
    alias_cli(cli)

    text = cli + " was successfully configured."
    return text

# sets up an alias for a cli so that it can be called directly by name (instead of calling it via the explicit huckle call) 
def alias_cli(cli):
    if not os.path.exists(dot_huckle_scripts + "/" + cli):
        g = open(dot_huckle_scripts + "/" + cli, "a+")
        os.chmod(dot_huckle_scripts + "/" + cli, 0o700)
        g.write("#!/bin/bash\n")
        g.write("huckle cli run " + cli + " \"$@\"")
        g.close

# initializes the configuration file of a given cli (initialized when a cli "created")
def init_configuration(cli, url):
    config_file_path = dot_huckle_config + "/" + cli + "/config"
    parser = ConfigParser()
    parser.readfp(StringIO(u"[default]"))

    if url is None:
        parser.set("default", "url", "")
    else:
        parser.set("default", "url", url)

    parser.set("default", "ssl.verify", "verify")
    parser.set("default", "url.pinning", "dynamic")

    with open(config_file_path, "w") as config:
        parser.write(config)

# verifies if a given configuration exists
def is_configured(file_path, contains):
    if contains in open(file_path).read():
        return True
    else:
        return False

# list all the installed clis
def list_clis():
    files = [f for f in listdir(dot_huckle_scripts) if isfile(join(dot_huckle_scripts, f))]
    for f in files:
        print(f) 

# remove a cli
def remove_cli(cli):
    if(path.exists(dot_huckle_scripts + "/" + cli)):
        os.remove(dot_huckle_scripts + "/" + cli)
        shutil.rmtree(dot_huckle_config + "/" + cli)
        print(cli + " was successfully removed.")
    else:
        print(cli + " is not installed.")

# remove a pinned url cache
def flush_pinned_urls(cli):
    pinned_file_path = dot_huckle_config + "/" + cli + "/pinned.json"
    if(path.exists(pinned_file_path)):
        os.remove(pinned_file_path)
        print(cli + ": pinned url cache was successfully flushed.")
    else:
        print(cli + ": no pinned url cache to flush.")

# lists all the configuration parameters of a cli
def config_list(cli):
    config_file_path = dot_huckle_config + "/" + cli + "/config"
    parser = ConfigParser()
    parser.read(config_file_path)

    for section_name in parser.sections():
        print("[" + section_name + "]")
        for name, value in parser.items(section_name):
            print('%s = %s' % (name, value))
        print
