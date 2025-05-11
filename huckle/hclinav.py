from subprocess import call
from restnavigator import Navigator
from functools import partial
from urllib.parse import urlparse, parse_qs, unquote

# avoid broken pipe signal crashing the program
from signal import signal, SIGPIPE, SIG_DFL
signal(SIGPIPE,SIG_DFL)

# huckle's imports
from huckle import config
from huckle import logger
from huckle.auth import credential
from huckle.auth import authenticator

import sys
import os
import fcntl
import json
import subprocess
import time
import requests
import errno
import socket
import certifi
import textwrap
import re
import shutil

try:
        from urllib import quote  # Python 2.X
except ImportError:
        from urllib.parse import quote  # Python 3+

logging = logger.Logger()


# produces a navigator that starts navigating from the root and with an api display name of apiname
def navigator(root, apiname):
    s = requests.Session()

    # ssl verify configuration check
    if config.ssl_verify == "verify":
        s.verify = certifi.where()
    elif config.ssl_verify == "skip":
        logging.warning("SSL verification is being skipped. This will leak credentials on the network if using authentication.")
        import warnings
        from urllib3.exceptions import InsecureRequestWarning
        warnings.simplefilter('ignore', InsecureRequestWarning)
        s.verify = False

#     if config.auth_mode == "basic":
#         logging.debug("HTTP Basic Authentication...")
#         credentials = credential.CredentialManager()
#         s.auth = requests.auth.HTTPBasicAuth(*(credentials.find()))
# 
#     elif config.auth_mode == "hcoak":
#         logging.debug("HCLI Core API Key Authentication...")
#         credentials = credential.CredentialManager()
#         s.auth = authenticator.HCOAKBearerAuth(*(credentials.hcoak_find()))

#     # Ensure root URL has proper scheme
#     if not root.lower().startswith(('http://', 'https://')):
#         # Add default http:// if no scheme is specified
#         root = 'http://' + root
#         logging.debug(f"huckle: no scheme specified, using: {root}")

    # For HTTPS URLs, add a fixed timeout to prevent indefinite stalling
    if root.lower().startswith('https://'):
        parsed_url = urlparse(root)
        hostname = parsed_url.netloc.split(':')[0]
        port = parsed_url.port or 443

        try:
            # Make a simple HEAD request with a short timeout
            # This will quickly reveal if HTTPS is working
            response = s.head(root, timeout=5)
            # If we get here, HTTPS is working fine
        except requests.exceptions.SSLError:
            # SSL errors mean the server is responding but has certificate issues
            # This is not a protocol mismatch, so continue
            pass
        except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout) as e:
            # Connection errors or timeouts might indicate protocol mismatch
            # If it's "connection reset" or similar, server is responding somehow
            error_str = str(e).lower()
            if "timed out" in error_str or "connection aborted" in error_str:
                # These specific errors often indicate protocol mismatch
                logging.warning("huckle: https connection appears to be stalled - possible protocol mismatch")
                http_url = root.replace('https://', 'http://', 1)
                error_msg = (f"{config.cliname}: https connection attempt stalled. "
                            f"The server at {hostname} may not support https. "
                            f"Try using {http_url}")
                raise Exception(error_msg)

    nav = Navigator.hal(root=root, apiname=apiname, session=s)

    return nav

# attempts to traverse through an hcli document with a command line argument
def traverse_argument(nav, arg):
    ilength = 0
    try:
        ilength = len(nav.links()["cli"])
    except Exception as warning:
        error = config.cliname + ": unable to navigate HCLI 1.0 compliant semantics. wrong url, or the service isn't running? " + str(nav.uri)
        raise Exception(error)

    for j, y in enumerate(nav.links()["cli"]):

        # we give first precedence to help so that help is easily accessible at all time.
        if arg == "help":
            if config.help_mode == "text":
                (content, path) = hcli_to_troff(nav, save_to_file=False)
                text = troff_to_text(content)
                return  ('stdout', text.encode('utf-8'))
            elif config.help_mode == "man":
                (content, path) = hcli_to_troff(nav, save_to_file=True)
                call(["man", path])
                sys.exit(0)

        # we give precedence to parameter traversal to help avoid forcing double quoting on the command line
        try:
            for k, l in enumerate(nav.links()["cli"][j]):
                hcli_type = l.links()["profile"][0].uri.split('#', 1)[1]
                if hcli_type == config.hcli_parameter_type:
                    if not (arg.startswith('\"') and arg.endswith('\"')):
                        arg = '\"' + arg + '\"'
                    nav = l["cli"][0](hcli_param=quote(arg))
                    return nav
        except:
            pass

        tempnav = nav.links()["cli"][j]
        try:
            if tempnav()["name"] == arg:
                nav = tempnav["cli"][0]
                return nav
        except:
            error = config.cliname + ": " + arg + ": " + "command not found."
            raise Exception(error)

        if j == ilength - 1:
            error = config.cliname + ": " + arg + ": " + "command not found."
            raise Exception(error)

# attempts to traverse through an execution. (only attempted when we've run out of command line arguments to parse)
def traverse_execution(nav):
    try:
        for k, z in enumerate(nav.links()["cli"]):
            tempnav = nav.links()["cli"][k]

            hcli_type = tempnav.links()["profile"][0].uri.split('#', 1)[1]
            if hcli_type == config.hcli_execution_type:
                method = tempnav()["http"]
                nav = tempnav["cli"][0]
                return flexible_executor(nav.uri, method)
    except KeyError:
        error = config.cliname + ": " + "command/parameter confusion. try escaping parameter: e.g., \\\"param\\\" or \\\'param\\\'."
        error += for_help()
        raise Exception(error)

    error = config.cliname + ": " + "unable to execute."
    error += for_help()
    raise Exception(error)

# attempts to pull at the root of the hcli to auto configure the cli
def install(url):
    nav = navigator(root=url, apiname="unknown")
    version = None
    try:
        version = nav()["hcli_version"]
    except Exception as warning:
        pass

    if version == "1.0":
        cli = nav()["name"]

        # Extract description from the section where name is "name"
        description = ""
        for section in nav().get("section", []):
            if section.get("name") == "name":
                description = section.get("description")
                break

        yield from config.create_configuration(cli, url, description)
    else:
        configurations = []
        for k, z in enumerate(nav.links()["cli"]):
            yield from install(nav.links()["cli"][k].uri)

            # Add separator after each HCLI except the last one
            if k < len(nav.links()["cli"]) - 1:
                yield ('stdout', b'\n')

# generates an OPTIONS and COMMANDS section to add to a text page
def options_and_commands_to_text(navigator):

    # This block outputs an OPTIONS section, in the man page, alongside each available option flag and its description
    options = ""
    option_count = 0
    for i, x in enumerate(navigator.links()["cli"]):
        tempnav = navigator.links()["cli"][i]
        hcli_type = tempnav.links()["profile"][0].uri.split('#', 1)[1]
        if hcli_type == config.hcli_option_type:
            option_count += 1
            options = options + "       " + tempnav()["name"] + "\n"
            options = options + "              " + tempnav()["description"] + "\n"
    if option_count > 0:
        options = "OPTIONS\n" + options

    # This block outputs a COMMANDS section, in the man page, alongside each available command and its description
    commands = ""
    command_count = 0
    for i, x in enumerate(navigator.links()["cli"]):
        tempnav = navigator.links()["cli"][i]
        hcli_type = tempnav.links()["profile"][0].uri.split('#', 1)[1]
        if hcli_type == config.hcli_command_type:
            command_count += 1
            commands = commands + "       " + tempnav()["name"] + "\n"
            commands = commands + "              " + tempnav()["description"] + "\n"
    if command_count > 0:
        commands = "COMMANDS\n" + commands

    return options + commands

# format hcli navigation to manpage like format
def hcli_to_troff(navigator, save_to_file=True):
    man_content = ""

    # Add the title header
    man_content += ".TH " + navigator()["name"].upper() + " 1 \n"

    # Process each section
    for i, x in enumerate(navigator()["section"]):
        section = navigator()["section"][i]
        man_content += ".SH " + section["name"].upper() + "\n"
        man_content += section["description"].replace("\\n\\n", "\n.sp\n") + "\n"

    # Add options and commands
    man_content += options_and_commands_to_man(navigator)

    # Save to file if requested
    file_path = None
    if save_to_file:
        millis = str(time.time())
        dynamic_doc_path = config.cli_manpage_path + "/" + config.cliname + "." + millis + ".man"
        config.create_folder(config.cli_manpage_path)
        config.create_file(dynamic_doc_path)

        with open(dynamic_doc_path, "w") as f:
            f.write(man_content)

        file_path = dynamic_doc_path

    return (man_content, file_path)

def man_to_txt(man_page):
    try:
        process = subprocess.run(['man', man_page], capture_output=True, text=True, check=True)
        process_col = subprocess.run(['col', '-b'], input=process.stdout, capture_output=True, text=True, check=True)
        return process_col.stdout
    except subprocess.CalledProcessError as e:
        error = "unable to convert help man page to text"
        raise Exception(error)

# generates an OPTIONS and COMMANDS section to add to a man page
def options_and_commands_to_man(navigator):
    # This block outputs an OPTIONS section, in the man page, alongside each available option flag and its description
    options = ""
    option_count = 0
    for i, x in enumerate(navigator.links()["cli"]):
        tempnav = navigator.links()["cli"][i]
        hcli_type = tempnav.links()["profile"][0].uri.split('#', 1)[1]
        if hcli_type == config.hcli_option_type:
            option_count += 1
            options = options + ".IP " + tempnav()["name"] + "\n"
            options = options + tempnav()["description"].replace("\\n\\n", "\n.sp\n") + "\n"
    if option_count > 0:
        options = ".SH OPTIONS\n" + options

    # This block outputs a COMMANDS section, in the man page, alongside each available command and its description
    commands = ""
    command_count = 0
    for i, x in enumerate(navigator.links()["cli"]):
        tempnav = navigator.links()["cli"][i]
        hcli_type = tempnav.links()["profile"][0].uri.split('#', 1)[1]
        if hcli_type == config.hcli_command_type:
            command_count += 1
            commands = commands + ".IP " + tempnav()["name"] + "\n"
            commands = commands + tempnav()["description"].replace("\\n\\n", "\n.sp\n") + "\n"
    if command_count > 0:
        commands = ".SH COMMANDS\n" + commands

    return options + commands

# standard error message to tell users to go check the help pages (man pages)
def for_help():
    text = ""
    text += "for help, use:\n\n"
    text += "  " + config.cliname + " help\n"
    text += "  " + config.cliname + " <command> help"
    return text

# a flexible executor that can work with the application/octet-stream media-type (per HCLI 1.0 spec)
def flexible_executor(url, method):
    # we take into account how a CLI should interact with SSL verification
    ssl_verify = "verify"
    if config.ssl_verify == "verify":
        ssl_verify = certifi.where()
    elif config.ssl_verify == "skip":
        ssl_verify = False

    # if we're configured to pin final urls, we setup the cache for future hits
    if config.url_pinning == "pin":
        parsed_url = urlparse(url)
        params = parse_qs(parsed_url.query)
        command_encoded = params.get('command', [None])[0]  # Returns a list, so take the first item
        if command_encoded:
            final_command = unquote(unquote(command_encoded))

            # Replace characters to match original format and pin the url
            final_command = final_command.replace('"', '').replace("'", r"\'")
            config.pin_url(final_command, url, method)
            logging.debug("pinned: [" + final_command + "] " + url + " " + method)

    auth_mode = None
    if config.auth_mode == "basic":
        credentials = credential.CredentialManager()
        auth_mode = requests.auth.HTTPBasicAuth(*(credentials.find()))
    elif config.auth_mode == "hcoak":
        credentials = credential.CredentialManager()
        auth_mode = authenticator.HCOAKBearerAuth(*(credentials.hcoak_find()))

    if method == "get":
        r = requests.get(url, stream=True, verify=ssl_verify, auth=auth_mode)
        return output_chunks(r)
    if method == "post":
        if not sys.stdin.isatty():

            logging.debug("Attempting to stream POST data...")
            headers = {'content-type': 'application/octet-stream'}
            stream = nbstdin()

            r = requests.post(url, data=stream.read(), headers=headers, stream=True, verify=ssl_verify, auth=auth_mode)
            return output_chunks(r)
        else:
            logging.debug("No data to stream. Empty POST data.")
            r = requests.post(url, data=None, stream=True, verify=ssl_verify, auth=auth_mode)
            return output_chunks(r)

    return

# outputs the response received from an execution
def output_chunks(response):
    if response.status_code >= 400:
        f = getattr(sys.stderr, 'buffer', sys.stderr)
        if response.headers['content-type'] == 'application/problem+json':
            try:
                problem_detail = json.loads(response.content)
                logging.error(problem_detail)
                error_msg = f"{problem_detail.get('detail', '')}"
                yield ('stderr', error_msg.encode('utf-8'))
            except (json.JSONDecodeError, KeyError) as error:
                raise Exception(error)
        else:
            for chunk in response.iter_content(16384):
                if chunk:
                    yield ('stderr', chunk)
    else:
        f = getattr(sys.stdout, 'buffer', sys.stdout)
        for chunk in response.iter_content(16384):
            if chunk:
                yield ('stdout', chunk)

# wraps stdin into a unbuffered generator
class nbstdin:
    def __init__(self):
        None

    def read(self):
        try:
            f = os.fdopen(sys.stdin.fileno(), 'rb', 0)
            logging.debug("huckle: It's likely a real command line environment stdin inputstream.")
            with f as fis:
                for chunk in iter(partial(fis.read, 16384), b''):
                    yield chunk
        except Exception as e:
            logging.debug("huckle: It's likely a huckle library use context. Falling back to an assumed doctored io.BytesIO inputstream.")
            for chunk in iter(partial(sys.stdin.read, 16384), b''):
                yield chunk

def troff_to_text(content, width=None):
    # If width is not specified, try to get the terminal size
    if width is None:
        try:
            columns, _ = shutil.get_terminal_size()
            width = columns
        except Exception:
            # Fall back to 80 if we can't determine terminal size
            width = 80

    # Helper function to handle troff escape characters
    def process_escapes(text):
        # Generic rule: remove backslash before any character
        text = re.sub(r'\\(.)', r'\1', text)
        return text

    # Extract the man page title from .TH line
    title_match = re.search(r'\.TH\s+(\S+)\s+(\S+)', content)
    if title_match:
        name = title_match.group(1)
        section = title_match.group(2)
        name_section = f"{name}({section})"
        centered_text = "User Commands"

        # Calculate proper alignment positions for header
        left_text = name_section
        center_text = centered_text
        right_text = name_section

        # Create properly aligned header
        left_part = left_text
        center_start = (width - len(center_text)) // 2
        center_part = " " * (center_start - len(left_part)) + center_text
        right_start = width - len(right_text)
        right_part = " " * (right_start - len(left_part) - len(center_part)) + right_text

        header = left_part + center_part + right_part

        # Create right-aligned footer
        footer = " " * (width - len(name_section)) + name_section
    else:
        header = ""
        footer = ""

    # Initialize result with header
    result = [header, ""] if header else []

    # Process the content line by line
    lines = content.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()

        if line.startswith('.B'):
            # For top-level .B directives, collect them as part of the next regular text
            # (we don't append to result yet)
            bold_text = line[2:].strip()
            i += 1
            # Continue processing to find any text that should follow this bold text
            continue

        # Process .SH (section header)
        if line.startswith('.SH'):
            # Add only a single blank line before section header
            if result and result[-1] != "":  # Only add if the last line isn't already blank
                result.append("")
            section_name = process_escapes(line[4:].strip().strip('"'))
            result.append(section_name)
            i += 1

            # Process the content until the next .SH or end
            section_content = []
            paragraph_lines = []

            while i < len(lines):
                current = lines[i].strip()

                # Check for next section header
                if current.startswith('.SH'):
                    break

                if current.startswith('.B'):
                    # Instead of creating a new line, add the bold text to the paragraph lines
                    bold_text = current[2:].strip()
                    if bold_text:
                        paragraph_lines.append(bold_text)
                    i += 1
                    continue

                # Process subsection header (.SS)
                if current.startswith('.SS'):
                    # Process any accumulated content before the subsection
                    if paragraph_lines:
                        # Join paragraph lines and then wrap
                        para_text = ' '.join(paragraph_lines)
                        # Width for wrapped text is the total width minus the indentation
                        wrapped_lines = textwrap.wrap(para_text, width=width-7)
                        for wrapped_line in wrapped_lines:
                            result.append(f"       {wrapped_line}")
                        result.append("")
                        paragraph_lines = []

                    # Add only a single blank line before subsection header
                    if result and result[-1] != "":  # Only add if the last line isn't already blank
                        result.append("")
                    # Add the subsection header
                    subsection_name = process_escapes(current[4:].strip().strip('"'))
                    result.append(f"   {subsection_name}")
                    i += 1
                    continue

                # Process indented paragraph (.IP)
                if current.startswith('.IP'):
                    # Process any accumulated content before the .IP
                    if paragraph_lines:
                        para_text = ' '.join(paragraph_lines)
                        wrapped_lines = textwrap.wrap(para_text, width=width-7)
                        for wrapped_line in wrapped_lines:
                            result.append(f"       {wrapped_line}")
                        paragraph_lines = []

                    # Add blank line before .IP entry
                    result.append("")

                    # Extract the item name
                    item_match = re.search(r'\.IP\s+"([^"]+)"', current)
                    if item_match:
                        item_name = process_escapes(item_match.group(1))
                    else:
                        item_name = process_escapes(current[3:].strip().strip('"'))

                    # Format for col -b style IP entries - less indentation, all the way to left margin
                    result.append(f"       {item_name}")
                    i += 1

                    # Collect the description lines
                    desc_text = []
                    while i < len(lines) and not (lines[i].strip().startswith('.') and 
                                               not lines[i].strip().startswith('.br') and 
                                               not lines[i].strip().startswith('.sp')):
                        if lines[i].strip().startswith('.sp'):
                            # Handle paragraph breaks
                            if desc_text:
                                # Wrap and add description with deeper indentation
                                wrapped_desc = textwrap.wrap(' '.join(desc_text), width=width-14)
                                for wrapped_line in wrapped_desc:
                                    result.append(f"              {wrapped_line}")
                                result.append("")
                                desc_text = []
                        elif lines[i].strip().startswith('.br'):
                            # Handle line breaks
                            if desc_text:
                                wrapped_desc = textwrap.wrap(' '.join(desc_text), width=width-14)
                                for wrapped_line in wrapped_desc:
                                    result.append(f"              {wrapped_line}")
                                desc_text = []
                        else:
                            # Regular text
                            if not lines[i].strip().startswith('.'):
                                desc_text.append(lines[i].strip())
                        i += 1

                    # Process the final description block
                    if desc_text:
                        wrapped_desc = textwrap.wrap(' '.join(desc_text), width=width-14)
                        for wrapped_line in wrapped_desc:
                            result.append(f"              {wrapped_line}")

                    continue

                # Handle paragraph breaks (.sp)
                if current.startswith('.sp'):
                    if paragraph_lines:
                        para_text = ' '.join(paragraph_lines)
                        wrapped_lines = textwrap.wrap(para_text, width=width-7)
                        for wrapped_line in wrapped_lines:
                            result.append(f"       {wrapped_line}")
                        result.append("")
                        paragraph_lines = []
                    i += 1
                    continue

                # Handle line breaks (.br)
                if current.startswith('.br'):
                    if paragraph_lines:
                        para_text = ' '.join(paragraph_lines)
                        wrapped_lines = textwrap.wrap(para_text, width=width-7)
                        for wrapped_line in wrapped_lines:
                            result.append(f"       {wrapped_line}")
                        paragraph_lines = []
                    i += 1
                    continue

                # Regular text (not a directive)
                if not current.startswith('.'):
                    # Process escape characters
                    processed_text = process_escapes(current)
                    paragraph_lines.append(processed_text)

                i += 1

            # Process any remaining section content
            if paragraph_lines:
                para_text = ' '.join(paragraph_lines)
                wrapped_lines = textwrap.wrap(para_text, width=width-7)
                for wrapped_line in wrapped_lines:
                    result.append(f"       {wrapped_line}")

            continue

        i += 1

    # Add footer with empty line before it
    if footer:
        result.append("")
        result.append(footer)

    return '\n'.join(result)
