from configparser import ConfigParser
from contextlib import contextmanager
from pathlib import Path
from io import StringIO
from os import listdir
from os.path import isfile, join
from os import path
import errno

# huckle's imports
from huckle import hutils

import os
import sys
import shutil
import json
import portalocker

root = os.path.abspath(os.path.dirname(__file__))
huckle_manpage_path = root + "/data/huckle.1"
home = os.path.expanduser("~")
dot_huckle = "%s/.huckle" % home
dot_huckle_tmp = dot_huckle + "/tmp"
dot_huckle_var = dot_huckle + "/var"
dot_huckle_var_log = dot_huckle_var + "/log"
dot_huckle_scripts = dot_huckle + "/bin"
dot_huckle_config = dot_huckle + "/etc"
dot_huckle_common_config_file_path = dot_huckle_config + "/config"
dot_bash_profile = home + "/.bash_profile"
dot_bashrc = home + "/.bashrc"
credentials_file_path = None
log_file_path = dot_huckle_var_log + "/huckle.log"

# These next variables are dynamically updated from read configuration. Be careful!
url = ""
cliname = "huckle"
cli_manpage_path = dot_huckle + "/tmp"
ssl_verify = "verify"
url_pinning = "dynamic"
credential_helper = "huckle"
auth_mode = "skip"
auth_user_profile = "default"
auth_apikey_profile = "default"

# URL Pinning lookup
pinned_urls = {}

# These hcli_ variables are taken from the semantic types found in the HCLI 1.0 specification
hcli_command_type = "command"
hcli_option_type = "option"
hcli_parameter_type = "parameter"
hcli_execution_type = "execution"

# parses the common huckle configuration to set configured execution
def parse_common_configuration():
    global dot_huckle_common_config_file_path
    common_config_file_path = dot_huckle_common_config_file_path

    parser = ConfigParser()
    parser.read(common_config_file_path)
    if parser.has_section("default"):
        for section_name in parser.sections():
            for name, value in parser.items("default"):
                if name == "log":
                    global log
                    log = value
                if name == "log.level":
                    global log_level
                    log_level = value
    else:
        sys.exit("huckle: no common configuration " + common_config_file_path + " available")

# parses the configuration of a given cli to set configured execution
def parse_configuration(cli):
    global credentials_file_path
    credentials_file_path = dot_huckle_config + "/" + cli + "/credentials"

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
                if name == "credential.helper":
                    global credential_helper
                    credential_helper = value
                if name == "auth.mode":
                    global auth_mode
                    auth_mode = value
                if name == "auth.user.profile":
                    global auth_user_profile
                    auth_user_profile = value
                if name == "auth.apikey.profile":
                    global auth_apikey_profile
                    auth_apikey_profile = value
            if url == "": sys.exit("huckle: no url defined for " + cli + " under " + config_file_path)
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
    with write_lock(pinned_file_path):
        with open(pinned_file_path, 'w') as file:
            json.dump(pinned_urls, file)

# creates a common configuration file for huckle
def create_common_configuration():
    global dot_huckle_common_config_file_path
    common_config_file_path = dot_huckle_common_config_file_path

    # create the configuration if it doesn't exist
    if not os.path.exists(common_config_file_path):
        create_file(common_config_file_path)
        init_common_configuration()
    else:
        pass

    return

# creates a configuration file for a named cli
def create_configuration(cli, url):
    global credentials_file_path
    credentials_file_path = dot_huckle_config + "/" + cli + "/credentials"

    config_file_folder = dot_huckle_config + "/" + cli
    config_file = config_file_folder + "/config"
    create_folder(config_file_folder)

    if not os.path.exists(config_file):
        create_file(config_file)
        init_configuration(cli, url)
    else:
        hutils.eprint("huckle: the configuration for " + cli + " already exists. leaving the existing configuration untouched.")
        sys.exit(1)

    create_folder(cli_manpage_path + "/huckle." + cli)
    alias_cli(cli)

    return

# sets up an alias for a cli so that it can be called directly by name (instead of calling it via the explicit huckle call) 
def alias_cli(cli):
    if not os.path.exists(dot_huckle_scripts + "/" + cli):
        g = open(dot_huckle_scripts + "/" + cli, "a+")
        os.chmod(dot_huckle_scripts + "/" + cli, 0o700)
        g.write("#!/bin/bash\n")
        g.write("huckle cli run " + cli + " \"$@\"")
        g.close

# initializes the common huckle configuration file
def init_common_configuration():
    global dot_huckle_common_config_file_path
    common_config_file_path = dot_huckle_common_config_file_path

    parser = ConfigParser()
    parser.read_file(StringIO(u"[default]"))
    parser.set("default", "log", "skip")
    parser.set("default", "log.level", "info")

    with open(common_config_file_path, "w") as config:
        parser.write(config)

# initializes the configuration file of a given cli (initialized when a cli "created")
def init_configuration(cli, url):
    global credentials_file_path
    credentials_file_path = dot_huckle_config + "/" + cli + "/credentials"

    config_file_path = dot_huckle_config + "/" + cli + "/config"
    parser = ConfigParser()
    parser.read_file(StringIO(u"[default]"))

    if url is None:
        parser.set("default", "url", "")
    else:
        parser.set("default", "url", url)

    parser.set("default", "ssl.verify", "verify")
    parser.set("default", "url.pinning", "dynamic")
    parser.set("default", "credential.helper", "huckle")
    parser.set("default", "auth.mode", "skip")
    parser.set("default", "auth.user.profile", "default")
    parser.set("default", "auth.apikey.profile", "default")

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
    else:
        hutils.eprint("huckle: " + cli + " is not installed.")
        sys.exit(1)

# remove a pinned url cache
def flush_pinned_urls(cli):
    pinned_file_path = dot_huckle_config + "/" + cli + "/pinned.json"
    if(path.exists(pinned_file_path)):
        os.remove(pinned_file_path)
    else:
        hutils.eprint("huckle: no pinned url cache to flush for " + cli + ".")
        sys.exit(1)

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

# update a configured parameter to a new value
def update_parameter(cli, parameter, value):
    config_file_path = dot_huckle_config + "/" + cli + "/config"
    parser = ConfigParser()
    parser.read(config_file_path)

    try:
        parser.set('default', parameter, value)
    except Exception as error:
        hutils.eprint("huckle: unable to update configuration")
        sys.exit(1)

    with write_lock(config_file_path):
        with open(config_file_path, "w") as config:
            parser.write(config)

# get a configured parameter
def get_parameter(cli, parameter):
    config_file_path = dot_huckle_config + "/" + cli + "/config"
    parser = ConfigParser()
    parser.read(config_file_path)

    try:
        return parser.get('default', parameter)
    except Exception as error:
        hutils.eprint("huckle: unable to retrieve configuration")
        sys.exit(1)

# creates a folder at "path"
def create_folder(path):
    with write_lock(path):
        if not os.path.exists(path):
            os.makedirs(path)

# creates a file at "path"
def create_file(path):
    with write_lock(path):
        if not os.path.exists(path):
            flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY

            try:
                file_handle = os.open(path, flags, 0o0600)
            except OSError as e:
                if e.errno == errno.EEXIST:  # Failed since the file already exists.
                    pass
                else:
                    raise
            else:
                with os.fdopen(file_handle, 'w') as file_obj:
                    file_obj.write("")
                    file_obj.close

@contextmanager
def write_lock(file_path):
    lockfile = Path(file_path).with_suffix('.lock')
    with portalocker.Lock(lockfile, timeout=10) as lock:
        yield

        # we cleanup the lock if successful.
        try:
            if lockfile.exists():
                os.unlink(lockfile)
        except OSError:
            pass
