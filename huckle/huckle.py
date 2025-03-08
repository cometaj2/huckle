from huckle import config
from huckle.auth import credential

import sys
import shlex
import io
from subprocess import call

from huckle import package
from huckle import hclinav
from huckle import logger

from contextlib import contextmanager

logging = logger.Logger()


# navigate through the command line sequence for a given cliname
def navigate(argv):
    nav = hclinav.navigator(root=config.url, apiname=config.cliname)

    # we try to fail fast if the service isn't reachable
    try:
        nav()["name"]
    except Exception as e:
        error = config.cliname + ": unable to navigate HCLI 1.0 compliant semantics. wrong url, or the service isn't running? " + str(nav.uri)
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

        if type(nav) == tuple:
            def generator():
                yield nav
            return generator()
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

# Execute CLI commands either from command line or as a library.
# Now checks if we're already in a stdin context.
def cli(commands=None):
    if commands is not None:
        needs_stdin = not isinstance(sys.stdin, io.BytesIO)

        if needs_stdin:
            with stdin(io.BytesIO(b'')):
                return __execute_cli(commands)
        else:
            return __execute_cli(commands)
    else:
        return __execute_cli(None)

# huckle's minimal set of commands
def __execute_cli(commands=None):
    if commands is not None:
        argv = shlex.split(commands)
    else:
        argv = sys.argv
        argv[0] = "huckle"

    if argv[0] == "huckle":
        pass
    else:
        config.parse_configuration(argv[0])
        return navigate(argv[0:])

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
            if len(argv) == 4:
                return config.config_list(argv[3])
            elif len(argv) == 5:
                return config.get_parameter(argv[3], argv[4])
            elif len(argv) == 6:
                return config.update_parameter(argv[3], argv[4], argv[5])
            else:
                return huckle_help()

        elif argv[1] == "cli" and argv[2] == "credential":
            if len(argv) == 5:
                if not sys.stdin.isatty():
                    secret = sys.stdin.read()

                    if isinstance(secret, bytes):
                        secret = secret.decode().strip()
                    else:
                        secret = secret.strip()

                    config.parse_configuration(argv[3])
                    credentials = credential.CredentialManager()
                    return credentials.update_credential(argv[4], secret)
                else:
                    return huckle_help()
            else:
                return huckle_help()

        elif argv[1] == "help":
            if config.help_mode == "text":
                with open(config.huckle_manpage_path, "r") as f:

                    text = f.read()
                    def generator():
                        yield ('stdout', hclinav.troff_to_text(text).encode('utf-8'))

                    return generator()
                f.close()
            elif config.help_mode == "man":
                call(["man", config.huckle_manpage_path])
                sys.exit(0)

        else:
            return huckle_help()

    elif len(argv) == 2:

        if argv[1] == "--version":
            return show_dependencies()

        elif argv[1] == "env":
            text = "export PATH=$PATH:" + config.dot_huckle_scripts + "\n\n"
            text += "# To point your shell to huckle's HCLI entrypoint scripts, run:\n"
            text += "# eval $(huckle env)"

            def generator():
                yield ('stdout', text.encode('utf-8'))

            return generator()

        elif argv[1] == "help":
            if config.help_mode == "text":
                with open(config.huckle_manpage_path, "r") as f:

                    text = f.read()
                    def generator():
                        yield ('stdout', hclinav.troff_to_text(text).encode('utf-8'))

                    return generator()
                f.close()
            elif config.help_mode == "man":
                call(["man", config.huckle_manpage_path])
                sys.exit(0)

        else:
            return huckle_help()

    else:
        return huckle_help()

def huckle_help():
    error = "for help, use:\n\n  huckle help"
    raise Exception(error)

# show huckle's version and the version of its dependencies

def show_dependencies():
    def parse_dependency(dep_string):
        # Common version specifiers
        specifiers = ['==', '>=', '<=', '~=', '>', '<', '!=']

        # Find the first matching specifier
        for specifier in specifiers:
            if specifier in dep_string:
                name, version = dep_string.split(specifier, 1)
                return name.strip(), specifier, version.strip()

        # If no specifier found, return just the name
        return dep_string.strip(), '', ''

    dependencies = ""
    for dep in package.dependencies:
        name, specifier, version = parse_dependency(dep)
        if version:  # Only add separator if there's a version
            dependencies += f" {name}/{version}"
        else:
            dependencies += f" {name}"

    def generator():
        yield ('stdout', f"huckle/{package.__version__}{dependencies}".encode('utf-8'))

    return generator()

def reconstruct_command(args):
    reconstructed = []
    for arg in args:
        # escape every single quote
        arg = arg.replace("'", "\\'")
        reconstructed.append(arg)
    return ' '.join(reconstructed)
