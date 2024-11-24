from huckle import hutils
from huckle import config
from huckle import logger

hutils.create_folder(config.dot_huckle)
hutils.create_folder(config.dot_huckle_config)
hutils.create_folder(config.dot_huckle_var_log)
hutils.create_folder(config.dot_huckle_scripts)
hutils.create_file(config.dot_bash_profile)

# create and load the common huckle configuration for logging before first log initialization
config.create_common_configuration()
config.parse_common_configuration()

# Map string log levels to logger constants
LOG_LEVELS = {
    'debug': logger.DEBUG,
    'info': logger.INFO,
    'warning': logger.WARNING,
    'error': logger.ERROR,
    'critical' : logger.CRITICAL
}
log_level = LOG_LEVELS.get(config.log_level.lower(), logger.INFO)

logging = logger.Logger(log=config.log)
logging.setLevel(log_level)

import sys
import shlex
import io

from huckle import package
from huckle import hclinav

from contextlib import contextmanager


# navigate through the command line sequence for a given cliname
def navigate(argv):
    nav = hclinav.navigator(root=config.url, apiname=config.cliname)

    # we try to fail fast if the service isn't reachable
    try:
        nav()["name"]
    except Exception as e:
        logging.error(e)
        error = config.cliname + ": unable to navigate HCLI 1.0 compliant semantics. wrong url, or the service isn't running? " + str(nav.uri)
        logging.error(error)
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
    if isinstance(stream, (str, bytes)):
        stream = io.BytesIO(stream.encode() if isinstance(stream, str) else stream)
    elif not hasattr(stream, 'read'):
        stream = io.BytesIO(b''.join(stream))

    sys.stdin = stream # Redirect sys.stdin to a provided io stream (e.g. io.BytesIO)

    try:
        yield

    finally:
        sys.stdin = sys.__stdin__

# huckle's minimal set of commands
def cli(commands=None):
    if commands is not None:
        argv = shlex.split(commands)
    else:
        argv = sys.argv
        argv[0] = "huckle"

    if argv[0] == "huckle":
        pass
    else:
        try:
            config.parse_configuration(argv[0])
            return navigate(argv[0:])
        except Exception as error:
            logging.error(error)
            raise Exception(error)

    if len(argv) > 2:

        if argv[1] == "cli" and argv[2] == "run":

            if len(argv) > 3:
                config.parse_configuration(argv[3])
                return navigate(argv[3:])

            else:
                return huckle_help()

        elif argv[1] == "cli" and argv[2] == "install":

            if len(argv) > 3:
                return hclinav.install(argv[3])

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
    hutils.eprint("for help, use:\n\n  huckle help")
    sys.exit(1)

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
