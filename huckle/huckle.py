from __future__ import absolute_import, division, print_function

import sys
import shlex
import io

# huckle's imports
from . import package
from . import config
from . import hclinav
from . import logger

from contextlib import contextmanager

logging = logger.Logger()


# navigate through the command line sequence for a given cliname
def navigate(argv):
    nav = hclinav.navigator(root=config.url, apiname=config.cliname)

    # we try to fail fast if the service isn't reachable
    try:
        nav()["name"]
    except Exception as warning:
        error = config.cliname + ": unable to navigate HCLI 1.0 compliant semantics. wrong HCLI or the service isn't running? " + str(nav.uri)
        raise Exception(error)

    # if we're configured for url pinning, we try to get a cache hit
    if config.url_pinning == "pin":
        command = reconstruct_command(argv)
        url, method = config.get_pinned_url(command)
        if url:
            logging.debug("found: [" + command + "] " + url + " " + method)
            return hclinav.flexible_executor(url, method)

    if len(argv) == 1:
        return hclinav.traverse_execution(nav)

    length = len(argv[1:])
    for i, x in enumerate(argv[1:]):
        nav = hclinav.traverse_argument(nav, x)

        if i == length - 1:
            return hclinav.traverse_execution(nav)

@contextmanager
def stdin(stream):
    sys.stdin = stream # Redirect sys.stdin to a provided io stream (e.g. io.BytesIO)

    try:
        yield

    finally:
        sys.stdin = sys.__stdin__

# huckle's minimal set of commands
def cli(commands):

    if commands is not None:
        argv = shlex.split(commands)
    else:
        argv = sys.argv
        argv[0] = "huckle"

    if argv[0] == "huckle":
        pass
    else:
        return huckle_help()

    if len(argv) > 2:

        if argv[1] == "cli" and argv[2] == "install":

            if len(argv) > 3:
                return hclinav.pull(argv[3])

            else:
                return huckle_help()

        elif argv[1] == "cli" and argv[2] == "run":

            if len(argv) > 3:
                config.parse_configuration(argv[3])
                return navigate(argv[3:])

            else:
                return huckle_help()

        elif argv[1] == "cli" and argv[2] == "ls":
            return config.list_clis()

        elif argv[1] == "cli" and argv[2] == "rm":
            if len(argv) > 3:
                return config.remove_cli(argv[3])

            else:
                return huckle_help()

        elif argv[1] == "cli" and argv[2] == "flush":
            if len(argv) > 3:
                return config.flush_pinned_urls(argv[3])

            else:
                return huckle_help()

        elif argv[1] == "cli" and argv[2] == "config":
            if len(argv) > 3:
                return config.config_list(argv[3])

            else:
                return huckle_help()

        elif argv[1] == "help":
            return hclinav.display_man_page(config.huckle_manpage_path)

        else:
            return huckle_help()

    elif len(argv) == 2:

        if argv[1] == "--version":
            return show_dependencies()

        elif argv[1] == "env":
            text = "export PATH=$PATH:" + config.dot_huckle_scripts + "\n\n"
            text += "# To point your shell to huckle's HCLI entrypoint scripts, run:\n"
            text += "# eval $(huckle env)"
            return text

        elif argv[1] == "help":
            return hclinav.display_man_page(config.huckle_manpage_path)

        else:
            return huckle_help()

    else:
        return huckle_help()

def huckle_help():
    return "for help, use:\n\n  huckle help"

# show huckle's version and the version of its dependencies
def show_dependencies():
    dependencies = ""
    for i, x in enumerate(package.dependencies):
        dependencies += " "
        dependencies += package.dependencies[i].rsplit('==', 1)[0] + "/"
        dependencies += package.dependencies[i].rsplit('==', 1)[1]
    return "huckle/" + package.__version__ + dependencies

def reconstruct_command(args):
    reconstructed = []
    for arg in args:
        # escape every single quote
        arg = arg.replace("'", "\\'")
        reconstructed.append(arg)
    return ' '.join(reconstructed)
