import sys
import config
import json

from restnavigator import Navigator

usage = """huck version 0.0.1.dev1

desciption:
    huck is a generic hypermedia client that provides a cli-like interaction with
    hypermedia APIs that abide by a specific hypermedia API CLI pattern.

synopsis:
    huck <command> [parameter]

commands:
    create [cliname]
    
    This allows you to alias into a new cli. Restarting the terminal
    is required since we're using a .bash_profile alias.
                   
    cli [cliname]
    
    Used to invoke a cli. Note that the [cliname] alias created with
    huck create [cliname] should be used instead, for brevity.
"""

def navigate(argv):
    h = Navigator.hal(config.url, apiname=config.cliname)
    if len(argv) == 1:
        display_docs(h)

    length = len(argv[1:])
    for i, x in enumerate(argv[1:]):
        h = h["command"].get_by("name", x)
        if h is None:
            print "ERROR: The \"" + x + "\" command is not available."
            break

        if i == length - 1:
            display_docs(h)

def display_docs(navigator):
    print navigator()["name"] + " version " + navigator()["version"] + "\n"
    print "description:"
    print "    " + navigator()["description"] + "\n" 

    print "synopsis:"
    print "    " + navigator()["synopsis"]["description"] + "\n"
    try:
        navigator()["option"]
        print "options:"
        for i, x in enumerate(navigator()["option"]):
            print "    " + navigator()["option"][i]["name"] + "\n"
            print "    " + navigator()["option"][i]["description"] + "\n"
    except:
        pass

    try:
        navigator()["command"]
        print "commands:"
        for i, x in enumerate(navigator()["command"]):
            print "    " + navigator()["command"][i]["name"] + "\n"
            print "    " + navigator()["command"][i]["description"] + "\n"
    except:
        pass

def pretty_json(navigator):
    print json.dumps(navigator(), indent=4, sort_keys=True)

def cli():
    if len(sys.argv) > 2:
        if sys.argv[1] == "cli":
            config.parse_configuration(sys.argv[2])
            navigate(sys.argv[2:])
        if sys.argv[1] == "create":
            config.create_configuration(sys.argv[2])
            config.alias_cli(sys.argv[2])
    else:
        sys.exit(usage)
