import sys
import config
import json

from restnavigator import Navigator

usage = """name:
    huckle

desciption:
    Huckle is a generic CLI that can be used with any API that abides by
    the standard hypertext command line interface (HCLI) semantics.

synopsis:
    huckle [options] <command> [parameter]

commands:
    create [cliname]
    
    This allows you to alias into a new CLI. Restarting the terminal
    is required since we're using a .bash_profile alias.
                   
    cli [cliname]
    
    Used to invoke a CLI. Note that the [cliname] alias created with
    huckle create [cliname] should be used instead, for brevity.

options:
    --version

    Huckle's version and the version of it's dependencies.

"""

def navigate(argv):
    h = Navigator.hal(config.url, apiname=config.cliname)
    if len(argv) == 1:
        display_docs(h)

    length = len(argv[1:])
    for i, x in enumerate(argv[1:]):
        h = h["command"].get_by("name", x)
        if h is None:
            print config.cliname + ": " + x + ": " + "command not found."
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
        else:
            sys.exit(usage)
    else:
        if len(sys.argv) == 2 and sys.argv[1] == "--version":
            dependencies = ""
            for i, x in enumerate(config.dependencies):
                dependencies += " "
                dependencies += config.dependencies[i].rsplit('==', 1)[0] + "/"
                dependencies += config.dependencies[i].rsplit('==', 1)[1]
            print "huckle/" + config.__version__ + dependencies
        else:
            sys.exit(usage)
