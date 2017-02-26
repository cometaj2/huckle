import sys
import config
import utils
import json
import subprocess
import time

from subprocess import call
from restnavigator import Navigator

def navigate(argv):
    nav = Navigator.hal(config.url, apiname=config.cliname)
    if len(argv) == 1:
        for_help()

    length = len(argv[1:])
    for i, x in enumerate(argv[1:]):

        ilength = 0
        try:
            ilength = len(nav.embedded()["item"])
        except:
            utils.eprint(config.cliname + ": unable to find a command, option, parameter or execution item to observe. bad hcli 1.0 server implementation.")
            sys.exit(1)

        for j, y in enumerate(nav.embedded()["item"]):
           
            tempnav = nav.embedded()["item"][j]
            if tempnav()["name"] == x:
                nav = tempnav["cli"][0]
                break

            if j == ilength - 1:
                if x == "help":
                    hcli_to_man(nav)
                    sys.exit(0)
                else:
                    utils.eprint(config.cliname + ": " + x + ": " + "command not found.")
                    sys.exit(2)

        if i == length - 1:
            utils.eprint(config.cliname + ": " + "command not found.")
            for_help()
            sys.exit(2)

def display_man_page(path):
    call(["man", path])

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

def pretty_json(json):
    print json.dumps(json, indent=4, sort_keys=True)

def for_help():
    utils.eprint("for help, use:\n")
    utils.eprint("  " + config.cliname + " help")
    utils.eprint("  " + config.cliname + " <command> help")

def cli():
    if len(sys.argv) > 2:
        if sys.argv[1] == "cli":
            config.parse_configuration(sys.argv[2])
            navigate(sys.argv[2:])
        elif sys.argv[1] == "create":
            config.create_configuration(sys.argv[2])
            config.alias_cli(sys.argv[2])
        elif sys.argv[1] == "help":
            display_man_page(config.huckle_manpage_path)
            sys.exit(0)
        else:
            utils.eprint("huckle: " + sys.argv[1] + ": command not found.")
            for_help()
            sys.exit(2)
    elif len(sys.argv) == 2:
        if sys.argv[1] == "--version":
            dependencies = ""
            for i, x in enumerate(config.dependencies):
                dependencies += " "
                dependencies += config.dependencies[i].rsplit('==', 1)[0] + "/"
                dependencies += config.dependencies[i].rsplit('==', 1)[1]
            print "huckle/" + config.__version__ + dependencies
        elif sys.argv[1] == "help":
            display_man_page(config.huckle_manpage_path)
            sys.exit(0)
        else:
            utils.eprint("huckle: " + sys.argv[1] + ": command not found.")
            for_help()
            sys.exit(2)
    else:
        for_help()
        sys.exit(2)
