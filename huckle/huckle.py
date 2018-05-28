from __future__ import absolute_import, division, print_function

# huckle's imports
from . import package
from . import config
from . import hutils
from . import hclinav

import sys

# navigate through the command line sequence for a given cliname
def navigate(argv):
    nav = hclinav.navigator(root=config.url, apiname=config.cliname)

    if len(argv) == 1:
        hclinav.traverse_execution(nav)

    length = len(argv[1:])
    for i, x in enumerate(argv[1:]):
        nav = hclinav.traverse_argument(nav, x)

        if i == length - 1:
            hclinav.traverse_execution(nav)

# huckle's minimal set of commands
def cli():

    if len(sys.argv) > 2:
    
        if sys.argv[1] == "cli" and sys.argv[2] == "install":
            
            if len(sys.argv) > 3:
                hclinav.pull(sys.argv[3])
                
            else:
                huckle_help()
            
        elif sys.argv[1] == "cli" and sys.argv[2] == "run":
                
            if len(sys.argv) > 3:
                config.parse_configuration(sys.argv[3])
                navigate(sys.argv[3:])

            else:
                huckle_help()

        elif sys.argv[1] == "help":
            hclinav.display_man_page(config.huckle_manpage_path)
            sys.exit(0)

        else:
            huckle_help()

    elif len(sys.argv) == 2:

        if sys.argv[1] == "--version":
            show_dependencies() 

        elif sys.argv[1] == "help":
            hclinav.display_man_page(config.huckle_manpage_path)
            sys.exit(0)

        else:
            huckle_help()

    else:
        huckle_help()

def huckle_help():
    hutils.eprint("for help, use:\n")
    hutils.eprint("  huckle help")
    sys.exit(2)

# show huckle's version and the version of its dependencies
def show_dependencies():
    dependencies = ""
    for i, x in enumerate(package.dependencies):
        dependencies += " "
        dependencies += package.dependencies[i].rsplit('==', 1)[0] + "/"
        dependencies += package.dependencies[i].rsplit('==', 1)[1]
    print("huckle/" + package.__version__ + dependencies)
