from __future__ import absolute_import, division, print_function

from subprocess import call
from restnavigator import Navigator
from functools import partial
from urllib.parse import urlparse, parse_qs, unquote

# avoid broken pipe signal crashing the program
from signal import signal, SIGPIPE, SIG_DFL 
signal(SIGPIPE,SIG_DFL) 

# huckle's imports
from . import config
from . import hutils
from . import logger

import sys
import os
import fcntl
import json
import subprocess
import time
import requests
import errno
import socket
import certifi

try:
        from urllib import quote  # Python 2.X
except ImportError:
        from urllib.parse import quote  # Python 3+

logging = logger.Logger()


# produces a navigator that starts navigating from the root and with an api display name of apiname
def navigator(root, apiname):
    s = requests.Session()

    if config.ssl_verify == "verify":
        s.verify = certifi.where()
    elif config.ssl_verify == "skip":
        #import warnings
        #from urllib3.exceptions import InsecureRequestWarning
        #warnings.simplefilter('ignore', InsecureRequestWarning)
        s.verify = False

    nav = Navigator.hal(root=root, apiname=apiname, session=s)

    return nav

# attempts to traverse through an hcli document with a command line argument
def traverse_argument(nav, arg):
    ilength = 0
    try:
        ilength = len(nav.links()["cli"])
    except Exception as warning:
        error = config.cliname + ": unable to navigate HCLI 1.0 compliant semantics. wrong HCLI or the service isn't running? " + str(nav.uri)
        raise Exception(error)

    for j, y in enumerate(nav.links()["cli"]):

        # we give first precedence to help so that help is easily accessible at all time.
        if arg == "help":
            hcli_to_man(nav)
            sys.exit(0)

        # we give precedence to parameter traversal to help avoid forcing double quoting on the command line
        try:
            for k, l in enumerate(nav.links()["cli"][j]):
                hcli_type = l.links()["profile"][0].uri.split('#', 1)[1]
                if hcli_type == config.hcli_parameter_type:
                    if not (arg.startswith('\"') and arg.endswith('\"')):
                        arg = '\"' + arg + '\"'
                    nav = l["cli"][0](hcli_param=quote(arg))
                    return nav
        except:
            pass

        tempnav = nav.links()["cli"][j]
        try:
            if tempnav()["name"] == arg:
                nav = tempnav["cli"][0]
                return nav
        except:
            error = config.cliname + ": " + arg + ": " + "command not found."
            raise Exception(error)

        if j == ilength - 1:
            error = config.cliname + ": " + arg + ": " + "command not found."
            raise Exception(error)

# attempts to traverse through an execution. (only attempted when we've run out of command line arguments to parse)
def traverse_execution(nav):
    try:
        for k, z in enumerate(nav.links()["cli"]):
            tempnav = nav.links()["cli"][k]

            hcli_type = tempnav.links()["profile"][0].uri.split('#', 1)[1]
            if hcli_type == config.hcli_execution_type:
                method = tempnav()["http"]
                nav = tempnav["cli"][0]
                return flexible_executor(nav.uri, method)
    except KeyError:
        error = config.cliname + ": " + "command/parameter confusion. try escaping parameter: e.g., \\\"param\\\" or \\\'param\\\'.\n"
        error += for_help()
        raise Exception(error)

    error = config.cliname + ": " + "unable to execute.\n"
    error += for_help()
    raise Exception(error)

# attempts to pull at the root of the hcli to auto configure the cli
def pull(url):
    nav = navigator(root=url, apiname="unknown")
    try:
        version = nav()["hcli_version"]
        if version == "1.0":
            cli = nav()["name"]

            text = ""
            try:
                text += hcli_to_text(nav)
                configuration = config.create_configuration(cli, url)
                return text + configuration
            except Exception as error:
                raise Exception(error)
    except Exception as warning:
        try:
            for k, z in enumerate(nav.links()["cli"]):
                return pull(nav.links()["cli"][k].uri)
        except Exception as warning:
            error = config.cliname + ": unable to navigate HCLI 1.0 compliant semantics. wrong HCLI or the service isn't running? " + str(nav.uri)
            raise Exception(error)

# displays a man page (file) located on a given path
def display_man_page(path):
    call(["man", path])

# converts an hcli document to a text and displays it
def hcli_to_text(navigator):
    text = ""
    for i, x in enumerate(navigator()["section"]):
        section = navigator()["section"][i]
        text += section["name"].upper() + "\n"
        text += "       " + section["description"] + "\n\n"
    text += options_and_commands_to_text(navigator)
    return text

# generates an OPTIONS and COMMANDS section to add to a text page
def options_and_commands_to_text(navigator):

    # This block outputs an OPTIONS section, in the man page, alongside each available option flag and its description
    options = ""
    option_count = 0
    for i, x in enumerate(navigator.links()["cli"]):
        tempnav = navigator.links()["cli"][i]
        hcli_type = tempnav.links()["profile"][0].uri.split('#', 1)[1]
        if hcli_type == config.hcli_option_type:
            option_count += 1
            options = options + "       " + tempnav()["name"] + "\n"
            options = options + "              " + tempnav()["description"] + "\n"
    if option_count > 0:
        options = "OPTIONS\n" + options

    # This block outputs a COMMANDS section, in the man page, alongside each available command and its description
    commands = ""
    command_count = 0
    for i, x in enumerate(navigator.links()["cli"]):
        tempnav = navigator.links()["cli"][i]
        hcli_type = tempnav.links()["profile"][0].uri.split('#', 1)[1]
        if hcli_type == config.hcli_command_type:
            command_count += 1
            commands = commands + "       " + tempnav()["name"] + "\n"
            commands = commands + "              " + tempnav()["description"] + "\n"
    if command_count > 0:
        commands = "COMMANDS\n" + commands

    return options + commands

# converts an hcli document to a man page and displays it
def hcli_to_man(navigator):
    millis = str(time.time())
    dynamic_doc_path = config.cli_manpage_path + "/" + config.cliname + "." + millis + ".man" 
    hutils.create_folder(config.cli_manpage_path)
    hutils.create_file(dynamic_doc_path)
    f = open(dynamic_doc_path, "a+")
    f.write(".TH " + navigator()["name"] + " 1 \n")
    for i, x in enumerate(navigator()["section"]):
        section = navigator()["section"][i]
        f.write(".SH " + section["name"].upper() + "\n")
        f.write(section["description"].replace("\\n", "\n") + "\n")
    f.write(options_and_commands_to_man(navigator))

    f.close()
    display_man_page(dynamic_doc_path)

# generates an OPTIONS and COMMANDS section to add to a man page
def options_and_commands_to_man(navigator):
    # This block outputs an OPTIONS section, in the man page, alongside each available option flag and its description
    options = ""
    option_count = 0
    for i, x in enumerate(navigator.links()["cli"]):
        tempnav = navigator.links()["cli"][i]
        hcli_type = tempnav.links()["profile"][0].uri.split('#', 1)[1]
        if hcli_type == config.hcli_option_type:
            option_count += 1
            options = options + ".IP " + tempnav()["name"] + "\n"
            options = options + tempnav()["description"].replace("\\n", "\n") + "\n"
    if option_count > 0:
        options = ".SH OPTIONS\n" + options

    # This block outputs a COMMANDS section, in the man page, alongside each available command and its description
    commands = ""
    command_count = 0
    for i, x in enumerate(navigator.links()["cli"]):
        tempnav = navigator.links()["cli"][i]
        hcli_type = tempnav.links()["profile"][0].uri.split('#', 1)[1]
        if hcli_type == config.hcli_command_type:
            command_count += 1
            commands = commands + ".IP " + tempnav()["name"] + "\n"
            commands = commands + tempnav()["description"].replace("\\n", "\n") + "\n"
    if command_count > 0:
        commands = ".SH COMMANDS\n" + commands

    return options + commands

# pretty json dump
def pretty_json(json):
    print(json.dumps(json, indent=4, sort_keys=True))

# standard error message to tell users to go check the help pages (man pages)
def for_help():
    text = ""
    text += "for help, use:\n\n"
    text += "  " + config.cliname + " help\n"
    text += "  " + config.cliname + " <command> help"
    return text

# a flexible executor that can work with the application/octet-stream media-type (per HCLI 1.0 spec)
def flexible_executor(url, method):
    # we take into account how a CLI should interact with SSL verification
    ssl_verify = "verify"
    if config.ssl_verify == "verify":
        ssl_verify = certifi.where()
    elif config.ssl_verify == "skip":
        ssl_verify = False

    # if we're configured to pin final urls, we setup the cache for future hits
    if config.url_pinning == "pin":
        parsed_url = urlparse(url)
        params = parse_qs(parsed_url.query)
        command_encoded = params.get('command', [None])[0]  # Returns a list, so take the first item
        if command_encoded:
            final_command = unquote(unquote(command_encoded))

            # Replace characters to match original format and pin the url
            final_command = final_command.replace('"', '').replace("'", r"\'")
            config.pin_url(final_command, url, method)
            logging.debug("pinned: [" + final_command + "] " + url + " " + method)

    if method == "get":
        r = requests.get(url, stream=True, verify=ssl_verify)
        return output_chunks(r)
    if method == "post":
        if not sys.stdin.isatty():

            headers = {'content-type': 'application/octet-stream'}
            stream = nbstdin()

            r = requests.post(url, data=stream.read(), headers=headers, stream=True, verify=ssl_verify)
            return output_chunks(r)
        else:
            r = requests.post(url, data=None, stream=True, verify=ssl_verify)
            return output_chunks(r)

    return

# outputs the response received from an execution
def output_chunks(response):
    if response.status_code >= 400:
        code = response.status_code
        error = str(code) + " " + requests.status_codes._codes[code][0] + "\n"
        error += str(response.headers) + "\n"
        error += str(response.content)
        raise Exception(error)
    else:
        f = getattr(sys.stdout, 'buffer', sys.stdout)
        for chunk in response.iter_content(16384):
            if chunk:
                yield chunk

# wraps stdin into a unbuffered generator
class nbstdin:
    def __init__(self):
        None

    def read(self):
        try:
            f = os.fdopen(sys.stdin.fileno(), 'rb', 0)
            with f as fis:
                for chunk in iter(partial(fis.read, 16384), b''):
                    yield chunk
        except Exception as e:
            for chunk in iter(partial(sys.stdin.read, 16384), b''):
                yield chunk
