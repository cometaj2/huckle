|pypi| |build status| |pyver|

Huckle
======

Huckle is a CLI, and python library, that can act as an impostor for any CLI expressed via hypertext
command line interface (HCLI) semantics.

----

Huckle provides a way for developers to interact with, or script around, any API that exposes HCLI
semantics, while providing dynamic and up to date in-band access to all the API/CLI documentation,
man page style, which showcases commands, options, and parameters available for execution.

Most, if not all, programming languages have a way to issue shell commands. With the help
of a generic HCLI client such as Huckle, APIs that make use of HCLI semantics are readily consumable
anywhere via the familiar CLI mode of operation, and this, without there being a need to write
a custom and dedicated CLI to interact with a specific API.

Huckle can also be used as a python library to interact with HCLI APIs via python code in much the
same way as would be the case in a bash terminal.

You can access a simple example HCLI service to play with huckle on http://hcli.io [1]

The HCLI Internet-Draft [2] is a work in progress by the author and 
the current implementation leverages hal+json alongside a static form of ALPS
(semantic profile) [3] to help enable widespread cross media-type support.

Help shape huckle and HCLI on the discussion list [4] or by raising issues on github!

[1] http://hcli.io

[2] https://github.com/cometaj2/I-D/tree/master/hcli

[3] http://alps.io

[4] https://groups.google.com/forum/#!forum/huck-hypermedia-unified-cli-with-a-kick

Install Python, pip and huckle
------------------------------

Huckle requires bash with access to man pages, Python and pip. Install a supported version of Python for your system.

Install huckle via Python's pip:

.. code-block:: console

    pip install huckle

Basic usage
-----------

huckle env

    This provides a sample environment configuration for your PATH environment variable. This can be permanently configured
    for your environment by adding the command 'eval $(huckle env) in your shell startup configuration
    (e.g. .bashrc, .bash_profile, .profile)

huckle cli install \<url>

    This attempts to auto create and configure a CLI name if provided with the root URL of an HCLI API.
    If successful, the CLI can be invoked by name, after updating the path (see 'huckle env'). You can permanently enable
    HCLI entrypoint scripts by adding 'eval $(huckle env) to your a ~/.bashrc, ~/.bash_profile, or ~/.profile.

    Note that an existing configuration file is left alone if the command is run multiple times 
    for the same CLI.

    An example HCLI that can be used with Huckle is available on hcli.io:
        - `<http://hcli.io/hcli/cli/jsonf?command=jsonf>`_ (HCLI root)  
        - `<http://hcli.io/hal/#/hcli/cli/jsonf?command=jsonf>`_ (HAL Browser navigation)

    Alternatively, a WSGI application can be stood up very quickly using sample HCLIs available via hcli_core `<https://pypi.org/project/hcli-core/>`_

huckle cli run \<cliname>

    This invokes the cliname to issue HCLI API calls; the details of which are left to API implementers.

    Commands, options and parameters are presented gradually, to provide users with a way to
    incrementally discover and learn how the CLI is used.

\<cliname> ...

    For brevity, the CLI name can and should be invoked directly rather than through "huckle cli run \<cliname>.

\<cliname> ... help

    The reserved "help" command can be used anywhere in a command line sequence to have huckle generate
    a man page from the last successfully received HCLI Document. This helps with CLI exploration.

huckle help

    This opens up a man page that describes how to use huckle.

Python Library - Basic Usage
----------------------------

Here's a basic flask PWA example that incorporates huckle usage as a python library to get data
from an HCLI data aggregation service called 'hleg' running locally on port 9000 and a jsonf HCLI hosted on hcli.io:

.. code-block:: python

    from __future__ import absolute_import, division, print_function

    import flask
    import config
    import json
    import logger
    import io

    from huckle.huckle import cli, stdin
    from flask import Flask, render_template, send_file, jsonify, Response

    logging = logger.Logger()
    logging.setLevel(logger.INFO)


    def webapp():
        app = Flask(__name__)

        @app.route('/')
        def index():
            try:
                cli("huckle cli install https://hcli.io/hcli/cli/jsonf?command=jsonf")

                hello = io.BytesIO(b'{"hello":"world"}')
                with stdin(hello):
                    chunks = cli("huckle cli run jsonf go")
                    json_string = ''.join(chunk.decode('utf-8') for chunk in chunks)
                    logging.info(json_string)

                logging.info(cli("huckle --version"))
                cli("huckle cli install 127.0.0.1:9000")

                chunks = cli("huckle cli run hleg ls")
                json_string = ''.join(chunk.decode('utf-8') for chunk in chunks)
                data = json.loads(json_string)

                return render_template('table.html', bills=data)

            except Exception as error:
                logging.error(error)

            return render_template('index.html')

        @app.route('/manifest.json')
        def serve_manifest():
            return app.send_static_file('manifest.json')

        @app.route('/sw.js')
        def serve_sw():
            return app.send_static_file('sw.js')

        return app


Configuration
-------------

Huckle uses small scripts under ~/.huckle/bin to enable CLIs to be invoked by name.

Huckle also uses CLI configuration files (e.g. ~/.huckle/etc/\<cliname>/config) to associate a specific
CLI to an HCLI API root URL and other CLI specific configuration.

Versioning
----------

This project makes use of semantic versioning (http://semver.org) and may make use of the "devx",
"prealphax", "alphax" "betax", and "rcx" extensions where x is a number (e.g. 0.3.0-prealpha1)
on github. Only full major.minor.patch releases will be pushed to pip from now on.

Supports
--------

- HTTP/HTTPS

- HCLI version 1.0 semantics for:

    - hal+json

- Automatic man page generation with the "help" command, anywhere in a CLI.

- Command line execution responses for

    - All media types

- Streaming:
 
    - Handles very large stdin/stdout streams (fixed chunk size of 16834)

- SOCKS tunneling through environment variables (ALL_PROXY)

- Auto configuration of a CLI when provided with an HCLI API root URL (e.g. huckle cli install `<http://hcli.io/hcli/cli/jsonf?command=jsonf>`_  

- Listing of installed CLIs

- Listing of the configuration of a CLI

- Auto discovery of cli link relations when attempting to install from a root resource that isn't an hcli-document.

- URL pinning/caching, and cache flushing, of successfully traversed final execution URLs, to speed up execution of already executed command sequences.

- Use as a python library along with simple stdin-and-stdout-like data streaming.

To Do
-----
- Fork restnavigator repo or otherwise adjust to use restnavigator with requests (single http client instead of two)

- Support help docs output in the absence of man pages (e.g. git-bash on Windows)

- Support HCLI version 1.0 semantics for: 

    - Collection+JSON
    - hal+xml
    - Uber
    - HTML
    - Siren
    - JSON-LD
    - JSON API
    - Mason

- Support stream configuration

    - sending and receiving streams (configurable via CLI config)
    - sending and receiving non-streams (configuration via CLI config)
    - chunk size for streams send/receive (configurable via CLI config)

- Support non-stream send/receive (via CLI configuration)

- Support various authentication and/or passthrough per CLI configuration  

    - HTTP Basic Auth  
    - HTTP Digest  
    - Oauth2  
    - X509 (HTTPS mutual authentication)  
    - AWS
    - SAML 

- Better implementation for huckle params/options handling

- Support for re-aliasing a CLI with additional huckle options (e.g. adding "--ssl-no-verify" to huckle cli jsonf's shell script)

- Support server certificate validation bypass (e.g. --ssl-no-verify. This is not secure but is sometimes useful to troubleshoot)  

- Support for viewing information about an HCLI root (e.g. huckle view `<http://hcli.io/hcli/cli/jsonf?command=jsonf>`_

- Support forward proxy configuration through proxy environment variables (HTTP_PROXY, HTTPS_PROXY)

- Support hcli name conflic resolution (use namespaces?)
  
    - View currently selected namespace (e.g. huckle ns)
    - Viewing namespace list (e.g. huckle ns list)
    - Selecting a namespace (e.g. huckle ns use abc)
    - Remove an entire namespace and all associated CLIs (e.g. huckle ns rm abc)
    - Support adding and removing CLIs to namespaces

- Support multipart/form-data for very large uploads (see requests-toolbelt)

- Support HCLI nativization

- Support for Huckle DEBUG mode

- Support better help output for python library use

- Support better Huckle configuration and HCLI customization for python library use

- Support full in memory configuration use to avoid filesystem files in a python library use context

- Add circleci tests for python library use (intput and output streaming)

- Support for clear hcli parameter values documentation (e.g. ssl & pin)

Bugs
----

- An old cache (pinned urls) can sometimes yield unexpected failures. This has been observed with hcli_hc.

.. |build status| image:: https://circleci.com/gh/cometaj2/huckle.svg?style=shield
   :target: https://circleci.com/gh/cometaj2/huckle
.. |pypi| image:: https://img.shields.io/pypi/v/huckle?label=huckle
   :target: https://pypi.org/project/huckle
.. |pyver| image:: https://img.shields.io/pypi/pyversions/huckle.svg
   :target: https://pypi.org/project/huckle
