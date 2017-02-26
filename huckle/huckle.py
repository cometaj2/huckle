import sys
import config
import json
import subprocess
import time

from subprocess import call
from restnavigator import Navigator

def navigate(argv):
    nav = Navigator.hal(config.url, apiname=config.cliname)
    if len(argv) == 1:
        print config.cliname + ": " + "command not found."
        print "to see help text, use:\n"
        print "  " + config.cliname + " help"
        print "  " + config.cliname + " <command> help"
        sys.exit(1)

    length = len(argv[1:])
    for i, x in enumerate(argv[1:]):

        ilength = 0
        try:
            ilength = len(nav.embedded()["item"])
        except:
            sys.exit(config.cliname + ": unable to find a command, option, parameter or execution item to observe. bad hcli 1.0 server implementation.")

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
                    print config.cliname + ": " + x + ": " + "command not found."
                    sys.exit(1)

        if i == length - 1:
            print config.cliname + ": " + "command not found."
            print "to see help text, use:\n"
            print "  " + config.cliname + " help"
            print "  " + config.cliname + " <command> help"
            sys.exit(1)

def display_docs(navigator):
    for i, x in enumerate(navigator()["section"]):
        print navigator()["section"][i]["name"].upper()
        print "    " + navigator()["section"][i]["description"] + "\n"

    try:
        for i, x in enumerate(navigator.embedded()["item"]):
            tempnav = navigator.embedded()["item"][i]
            print tempnav()["name"]
            print "    " + tempnav()["description"] + "\n"
    except:
        pass

def display_man_page(path):
    call(["man", path])

def hcli_to_man(navigator):
    millis = str(time.time())
    dynamic_doc_path = config.cli_manpage_path + "/" + config.cliname + "." + millis + ".man" 
    config.create_file(dynamic_doc_path)
    f = open(dynamic_doc_path, "a+")
    f.write(".TH " + navigator()["name"] + " 1 \n")
    for i, x in enumerate(navigator()["section"]):
        f.write(".SH " + navigator()["section"][i]["name"].upper() + "\n")
        f.write(navigator()["section"][i]["description"] + "\n")

    #try:
    #    for i, x in enumerate(navigator.embedded()["item"]):
    #        tempnav = navigator.embedded()["item"][i]
    #        print tempnav()["name"]
    #        print "    " + tempnav()["description"] + "\n"
    #except:
    #    pass
    f.close()
    display_man_page(dynamic_doc_path)

def pretty_json(json):
    print json.dumps(json, indent=4, sort_keys=True)

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
            print "huckle: " + sys.argv[1] + ": command not found."
            print "to see help text, use: huckle help"
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
            print "huckle: " + sys.argv[1] + ": command not found."
            print "to see help text, use: huckle help"
            sys.exit(2)
    else:
        print "to see help text, use: huckle help"
        sys.exit(2)
