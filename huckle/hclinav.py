import sys
import config
import utils
import json
import subprocess
import time
import httplib2
import urllib

from subprocess import call
from restnavigator import Navigator

# produces a navigator that starts navigating from the root and with an api display name of apiname
def navigator(root, apiname):
    nav = Navigator.hal(config.url, apiname=config.cliname)
    return nav

# attempts to traverse through an hcli document with a command line argument
def traverse_argument(nav, arg):        
    ilength = 0
    try:
        ilength = len(nav.embedded()["item"])
    except:
        utils.eprint(config.cliname + ": unable to find a command, option, parameter or execution item to observe. bad or inexistent hcli 1.0 server implementation.")
        sys.exit(1)

    for j, y in enumerate(nav.embedded()["item"]):
           
        tempnav = nav.embedded()["item"][j]
            
        try:
            if tempnav()["name"] == arg:
                nav = tempnav["cli"][0]
                return nav
        except:
            if arg == "help":
                hcli_to_man(nav)
                sys.exit(0)
            else:
                hcli_type = tempnav.links()["type"][0].uri.split('#', 1)[1]
                if hcli_type == config.hcli_parameter_type:
                    nav = tempnav["cli"][0](hcli_param=urllib.quote(arg))
                    return nav
                else:
                    utils.eprint(config.cliname + ": " + arg + ": " + "command not found.")
                    sys.exit(2)

        if j == ilength - 1:
            if arg == "help":
                hcli_to_man(nav)
                sys.exit(0)
            else:
                utils.eprint(config.cliname + ": " + arg + ": " + "command not found.")
                sys.exit(2)

# attempts to traverse through a safe or unsafe execution. (only invoked when we've run out of command line arguments to parse)
def traverse_execution(nav):
    for k, z in enumerate(nav.embedded()["item"]):
        tempnav = nav.embedded()["item"][k]

        hcli_type = tempnav.links()["type"][0].uri.split('#', 1)[1]
        if hcli_type == config.hcli_safe_type:
            nav = tempnav["cli"][0]
            print json.dumps(nav())
            sys.exit(0)

        if hcli_type == config.hcli_unsafe_type:
            nav = tempnav["cli"][0].create()
            print json.dumps(nav())
            sys.exit(0)

    utils.eprint(config.cliname + ": " + "unable to execute.")
    for_help()
    sys.exit(2)

# displays a man page (file) located on a given path
def display_man_page(path):
    call(["man", path])

# converts an hcli document to a man page and displays it
def hcli_to_man(navigator):
    millis = str(time.time())
    dynamic_doc_path = config.cli_manpage_path + "/" + config.cliname + "." + millis + ".man" 
    utils.create_file(dynamic_doc_path)
    f = open(dynamic_doc_path, "a+")
    f.write(".TH " + navigator()["name"] + " 1 \n")
    for i, x in enumerate(navigator()["section"]):
        section = navigator()["section"][i]
        if section["name"].upper() == "EXAMPLES":
            f.write(options_and_commands(navigator))
        f.write(".SH " + section["name"].upper() + "\n")
        f.write(section["description"] + "\n")
    
    f.close()
    display_man_page(dynamic_doc_path)

# generates an OPTIONS and COMMANDS section to add to a man page
def options_and_commands(navigator):
    # This block outputs an OPTIONS section, in the man page, alongside each available option flag and its description
    options = ""
    option_count = 0
    for i, x in enumerate(navigator.embedded()["item"]):
        tempnav = navigator.embedded()["item"][i]
        hcli_type = tempnav.links()["type"][0].uri.split('#', 1)[1]
        if hcli_type == config.hcli_option_type:
            option_count += 1
            options = options + ".IP " + tempnav()["name"] + "\n"
            options = options + tempnav()["description"] + "\n"
    if option_count > 0:
        options = ".SH OPTIONS\n" + options

    # This block outputs a COMMANDS section, in the man page, alongside each available command and its description
    commands = ""
    command_count = 0
    for i, x in enumerate(navigator.embedded()["item"]):
        tempnav = navigator.embedded()["item"][i]
        hcli_type = tempnav.links()["type"][0].uri.split('#', 1)[1]
        if hcli_type == config.hcli_command_type:
            command_count += 1
            commands = commands + ".IP " + tempnav()["name"] + "\n"
            commands = commands + tempnav()["description"] + "\n"
    if command_count > 0:
        commands = ".SH COMMANDS\n" + commands
 
    return options + commands

# pretty json dump
def pretty_json(json):
    print json.dumps(json, indent=4, sort_keys=True)

# standard error message to tell users to go check the help pages (man pages)
def for_help():
    utils.eprint("for help, use:\n")
    utils.eprint("  " + config.cliname + " help")
    utils.eprint("  " + config.cliname + " <command> help")
