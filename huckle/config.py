import errno
import os
import sys
import shutil
import json
import portalocker

from configparser import ConfigParser
from contextlib import contextmanager
from pathlib import Path
from io import StringIO
from os import listdir
from os.path import isfile, join
from os import path

root = os.path.abspath(os.path.dirname(__file__))
huckle_manpage_path = root + "/data/huckle.1"
home = os.getenv('HUCKLE_HOME') or os.path.expanduser("~")
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
                if name == "help":
                    global help_mode
                    help_mode = value
                if name == "protocol.mismatch.timeout":
                    global protocol_mismatch_timeout
                    protocol_mismatch_timeout = value
    else:
        error = f"huckle: no common configuration {common_config_file_path} available."
        raise Exception(error)

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
            if url == "":
                error = f"huckle: no url defined for {cli} under {config_file_path}."
                raise Exception(error)
    else:
        error = f"huckle: no cli configuration {config_file_path} available for {cli}."
        raise Exception(error)

    pinned_file_path = dot_huckle_config + "/" + cli + "/pinned.json"
    try:
        with open(pinned_file_path, 'r') as file:
            global pinned_urls
            pinned_urls = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        pinned_urls = {}

    def success_generator():
        yield ('stdout', b'')

    return success_generator()

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
def create_configuration(cli, url, description):
    global credentials_file_path
    credentials_file_path = dot_huckle_config + "/" + cli + "/credentials"
    config_file_folder = dot_huckle_config + "/" + cli
    config_file = config_file_folder + "/config"

    try:
        create_folder(config_file_folder)
    except Exception as e:
        error = repr(e)
        logging.error(error)

    if not os.path.exists(config_file):
        try:
            create_file(config_file)
            init_configuration(cli, url, description)
            create_folder(cli_manpage_path + "/huckle." + cli)
            alias_cli(cli)
        except Exception as e:
            error = repr(e)
            logging.error(error)
    else:
        error = f"huckle: the configuration for {cli} already exists. leaving the existing configuration untouched."
        raise Exception(error)

    def success_generator():
        yield ('stdout', f"{cli}".encode('utf-8'))

    return success_generator()

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
    parser.set("default", "help", "text")
    parser.set("default", "protocol.mismatch.timeout", "5")

    with open(common_config_file_path, "w") as config:
        parser.write(config)

# initializes the configuration file of a given cli (initialized when a cli "created")
def init_configuration(cli, url, description):
    global credentials_file_path
    credentials_file_path = dot_huckle_config + "/" + cli + "/credentials"

    config_file_path = dot_huckle_config + "/" + cli + "/config"
    parser = ConfigParser()
    parser.read_file(StringIO(u"[default]"))

    if url is None:
        parser.set("default", "url", "")
    else:
        parser.set("default", "url", url)

    parser.set("default", "description", description)
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

def get_description(config_path):
    parser = ConfigParser()
    parser.read(config_path)

    description = ""
    if parser.has_section("default"):
        for section_name in parser.sections():
            for name, value in parser.items("default"):
                if name == "description":
                    return value

    return ""

# list all the installed clis
def list_clis():
    def generator():
        try:
            files = [f for f in listdir(dot_huckle_scripts) if isfile(join(dot_huckle_scripts, f))]

            # Handle empty list case first
            if not files:
                yield ('stdout', b'')
                return

            # Find the longest CLI name for padding calculation
            longest_name = max(len(f) for f in files) if files else 0
            # Set column width with exactly 2 spaces after the longest name
            column_width = longest_name + 2

            # Calculate terminal width (fallback to 80 if can't determine)
            terminal_width = 80
            try:
                import shutil
                terminal_width = shutil.get_terminal_size().columns
            except:
                pass  # Use default 80 if we can't get the terminal width

            # Leave some space for the HCLI column and spacing
            desc_max_width = terminal_width - column_width - 2

            # Format and output header
            yield ('stdout', f"{'HCLI':<{column_width}}DESCRIPTION\n".encode('utf-8'))

            # Output all but last item with newlines
            for f in files[:-1]:
                config_path = dot_huckle_config + "/" + f + "/config"
                description = get_description(config_path)

                # Truncate description if needed to fit in terminal
                if desc_max_width > 10 and len(description) > desc_max_width:
                    description = description[:desc_max_width-3] + "..."

                yield ('stdout', f"{f:<{column_width}}{description}\n".encode('utf-8'))

            # Last item without newline
            if files:
                f = files[-1]
                config_path = dot_huckle_config + "/" + f + "/config"
                description = get_description(config_path)

                # Truncate description if needed to fit in terminal
                if desc_max_width > 10 and len(description) > desc_max_width:
                    description = description[:desc_max_width-3] + "..."

                yield ('stdout', f"{f:<{column_width}}{description}".encode('utf-8'))

        except Exception as e:
            error = f"huckle: error listing clis: {str(e)}"
            raise Exception(error)

    return generator()

# remove a cli
def remove_cli(cli):
    script_path = dot_huckle_scripts + "/" + cli
    config_path = dot_huckle_config + "/" + cli

    def generator():
        if path.exists(script_path):
            os.remove(script_path)
            shutil.rmtree(config_path)
            yield ('stdout', b'')
        elif path.exists(config_path):
            shutil.rmtree(config_path)
            error = f"huckle: {cli} was not installed, however some configuration remained and is now cleanly deleted."
            raise Exception(error)
        else:
            error = f"huckle: {cli} is not installed."
            raise Exception(error)

    return generator()

# remove a pinned url cache
def flush_pinned_urls(cli):
    pinned_file_path = dot_huckle_config + "/" + cli + "/pinned.json"

    def generator():
        if path.exists(pinned_file_path):
            try:
                os.remove(pinned_file_path)
                yield ('stdout', b'')
            except Exception as e:
                error = f"huckle: error flushing pinned urls: {str(e)}"
                raise Exception(error)
        else:
            error = f"huckle: no pinned url cache to flush for {cli}."
            raise Exception(error)

    return generator()

# lists all the configuration parameters of a cli
def config_list(cli):
    config_file_path = dot_huckle_config + "/" + cli + "/config"
    parser = ConfigParser()
    parser.read(config_file_path)

    def generator():
        try:
            # Get all content first
            all_lines = []
            for section_name in parser.sections():
                all_lines.append(f"[{section_name}]")
                for name, value in parser.items(section_name):
                    all_lines.append(f'{name} = {value}')

            # Handle empty case
            if not all_lines:
                yield ('stdout', b'')
                return

            # Output all but last line with newlines
            for line in all_lines[:-1]:
                yield ('stdout', f"{line}\n".encode('utf-8'))

            # Output last line without newline
            if all_lines:
                yield ('stdout', all_lines[-1].encode('utf-8'))

        except Exception as error:
            error = "huckle: unable to list configuration."
            raise Exception(error)

    return generator()

# update a configured parameter to a new value
def update_parameter(cli, parameter, value):
    config_file_path = dot_huckle_config + "/" + cli + "/config"
    parser = ConfigParser()
    parser.read(config_file_path)

    def generator():
        try:
            parser.set('default', parameter, value)
            with write_lock(config_file_path):
                with open(config_file_path, "w") as config:
                    parser.write(config)
            yield ('stdout', b'')
        except Exception as error:
            error = "huckle: unable to update configuration."
            raise Exception(error)

    return generator()

# get a configured parameter
def get_parameter(cli, parameter):
    config_file_path = dot_huckle_config + "/" + cli + "/config"
    parser = ConfigParser()
    parser.read(config_file_path)

    def generator():
        try:
            value = parser.get('default', parameter)
            yield ('stdout', value.encode('utf-8'))
        except Exception as error:
            error = "huckle: unable to retrieve configuration."
            raise Exception(error)

    return generator()

# creates a folder at "path"
def create_folder(path):

    # Skip lock only if this is the actual user's home directory (not a custom HUCKLE_HOME)
    if path == os.path.expanduser("~"):
        if not os.path.exists(path):
            os.makedirs(path)
        return

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

create_folder(home)
create_folder(dot_huckle)
create_folder(dot_huckle_tmp)
create_folder(dot_huckle_config)
create_folder(dot_huckle_var)
create_folder(dot_huckle_var_log)
create_folder(dot_huckle_scripts)
create_file(dot_bash_profile)

# create and load the common huckle configuration for logging before first log initialization
create_common_configuration()
parse_common_configuration()

# we load the logger after the configuration is in otherwise we get no logger
from huckle import logger

# Map string log levels to logger constants
LOG_LEVELS = {
    'debug': logger.DEBUG,
    'info': logger.INFO,
    'warning': logger.WARNING,
    'error': logger.ERROR,
    'critical' : logger.CRITICAL
}

log_level = LOG_LEVELS.get(log_level.lower(), logger.INFO)
logging = logger.Logger(log=log)
logging.setLevel(log_level)
