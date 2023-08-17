from __future__ import absolute_import, division, print_function

# huckle's imports
from . import package
from . import config
from . import hutils
from . import hclinav
from . import logger

import sys

logging = logger.Logger()


# navigate through the command line sequence for a given cliname
def navigate(argv):
    nav = hclinav.navigator(root=config.url, apiname=config.cliname)

    # we try to fail fast if the service isn't reachable
    try:
        nav()["name"]
    except Exception as warning:
        #hutils.eprint(warning)
        hutils.eprint(config.cliname + ": unable to navigate HCLI 1.0 compliant semantics. wrong HCLI or the service isn't up? " + str(nav.uri))
        sys.exit(1)

    # if we're configured for url pinning, we try to get a cache hit
    if config.url_pinning == "pin":
        command = reconstruct_command(argv)
        url, method = config.get_pinned_url(command)
        if url:
            logging.debug("found: [" + command + "] " + url + " " + method)
            hclinav.flexible_executor(url, method)
            sys.exit(0)

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

        elif sys.argv[1] == "cli" and sys.argv[2] == "ls":
            config.list_clis()

        elif sys.argv[1] == "cli" and sys.argv[2] == "rm":
            if len(sys.argv) > 3:
                config.remove_cli(sys.argv[3])

            else:
                huckle_help()

        elif sys.argv[1] == "cli" and sys.argv[2] == "flush":
            if len(sys.argv) > 3:
                config.flush_pinned_urls(sys.argv[3])

            else:
                huckle_help()

        elif sys.argv[1] == "cli" and sys.argv[2] == "config":
            if len(sys.argv) > 3:
                config.config_list(sys.argv[3])

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

        elif sys.argv[1] == "env":
            print("export PATH=$PATH:" + config.dot_huckle_scripts)
            print("")
            print("# To point your shell to huckle's HCLI entrypoint scripts, run:")
            print("# eval $(huckle env)")

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

def reconstruct_command(args):
    reconstructed = []
    for arg in args:
        # escape every single quote
        arg = arg.replace("'", "\\'")
        reconstructed.append(arg)
    return ' '.join(reconstructed)
