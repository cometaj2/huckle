Huckle (hypermedia unified CLI... with a kick) |build status|_ |pypi|_ 
============================================

Huckle is a CLI that can act as an impostor for any CLI expressed via hypertext
command line interface (HCLI) semantics.

----

Huckle provides a dynamic view of the CLI documentation (man page style), and
execution of commands, options, and parameters that can be issued to an API
that exposes CLIs via HCLI semantics [1].

Most, if not all, programming languages have a way to issue shell commands. This makes
APIs that make use of HCLI semantics readily consumable anywhere via the familiar
CLI mode of operation, and this, without there being a need to write a custom and dedicated CLI.

With Huckle's help, developers can experiment quickly with any API that exposes HCLI
semantics, while providing in-band access to all the API/CLI documentation which showcases options,
command and parameters available for use.

The standard HCLI Internet-Draft [1] is a work in progress by the author and 
The current implementation leverages hal+json alongside a static form of ALPS
(semantic profile) [2] to help enable widespread cross media-type support.

You can access a simple example HCLI server to play with huckle [3]

Help shape huckle and HCLI on the discussion list [4] or by raising issues on github!

[1] https://github.com/cometaj2/I-D/tree/master/hcli

[2] http://alps.io

[3] https://hcli.io

[4] https://groups.google.com/forum/#!forum/huck-hypermedia-unified-cli-with-a-kick

Install Python, pip and huckle
-------------------

Huckle requires bash with access to man pages, Python 2.7, 3.3-3.6 and pip

  - Install any one version of Python 2.7, 3.3-3.6 for your system

Install pip (if it didn't get install alongside Python). For example:

  - curl -O https://bootstrap.pypa.io/get-pip.py
  - python get-pip.py

Install huckle

  - pip install huckle

Usage
-----

huckle pull \<url>

    This attempts to auto create and configure a CLI if provided with the root URL of an HCLI API.
    If successful, the CLI can be invoked by name, after restarting the terminal, as if created via
    "huckle create".
    
    Note that an existing configuration file is left alone if the command is run multiple times 
    for the same CLI.

    An example CLI that can be used with Huckle is available on hcli.io:
        - https://hcli.io/hcli-webapp/cli/jsonf?command=jsonf (HCLI root)  
        - https://hcli.io/hal/#/hcli-webapp/ (HAL Browser navigation)  

huckle create \<cliname>

    This manually creates a new cliname alias and configuration file. Once a CLI is created via huckle,
    it can be invoked by name directly after restarting the terminal. Note that further manual
    configuration of the URL of the HCLI root is required when using "huckle create".
   
    Also note that an existing configuration file is left alone if the command is run multiple times 
    for the same cliname.

huckle cli \<cliname>

    This invokes the cliname to issue HCLI API calls; the details of which are left to API implementers.
    
    Commands, options and parameters are presented gradually, to provide users with a way to
    incrementally discover and learn how the CLI is used.

\<cliname> ...

    For brevity, the CLI name can and should be invoked directly rather than through "huckle cli \<cliname>.

\<cliname> ... help

    The reserved "help" command can be used anywhere in a command line sequence to have huckle generate
    a man page from the last successfully received HCLI Document. This helps with CLI exploration.

huckle help

    This opens up a man page that describes how to use huckle.

Configuration
-------------

Huckle uses small scripts under ~/.huckle/bin to allow for CLIs to be kicked off by name.

Huckle also uses CLI configuration files (e.g. ~/.huckle/etc/\<cliname>/config) to associate a specific
CLI to a hypermedia API URL root and other CLI specific configuration.

Each CLI configuration file contains:
- A URL to the root of the hypermedia CLI API

Versioning
----------

Huckle uses semantic versioning (http://semver.org) and may make use of the "devx", "prealphax", "alphax"
"betax", and "rcx" extensions where x is a number (e.g. 0.3.0-prealpha1) on github. Only full
major.minor.patch releases will be pushed to pip from now on.

Supports
--------

- HCLI version 1.0 semantics for:

    - hal+json

- Automatic man page generation with the "help" command, anywhere in a CLI.

- Command line execution responses for:

    - All media types

- Streaming:
 
    - Handles very large stdin/stdout streams (fixed chunk size of 16834)

- Error output to stderr on client response status code >= 400

- SOCKS tunneling through environment variables (ALL_PROXY)

- Auto configuration of an HCLI when provided with a url to an HCLI root (e.g. huckle pull https://hcli.io/hcli-webapp/cli/jsonf?command=jsonf)  

To Do
-----
- Fork restnavigator repo or otherwise adjust to use restnavigator with requests (single http client instead of two)

- Support help docs output in the absence of man pages (e.g. git-bash on Windows)

- Support HCLI version 1.0 semantics for: 

    - Collection+JSON
    - hal+xml
    - HTML
    - Siren
    - JSON API
    - JSON-LD
    - Mason

- Support stream configuration

    - sending and receiving streams (configurable via CLI config)
    - sending and receiving non-streams (configuration via CLI config)
    - chunk size for streams send/receive (configurable via CLI config)

- Support non-stream send/receive (via CLI configuration)

- Support various authentication per CLI configuration  

    - HTTP Basic Auth  
    - HTTP Digest  
    - Oauth  
    - X509 (HTTPS mutual authentication)  
    - AWS
    - SAML 

- Support server certificate validation bypass (e.g. --ssl-no-verify. This is not secure but is sometimes useful to troubleshoot)  

- Support forward proxy configuration through proxy environment variables (HTTP_PROXY, HTTPS_PROXY)

- Support hcli name conflic resolution (brainstorm implementation; alias or rename?)

Bugs
----

None are known... so far.

.. |build status| image:: https://travis-ci.org/cometaj2/huckle.svg?branch=master
.. _build status: https://travis-ci.org/cometaj2/huckle
.. |pypi| image:: https://badge.fury.io/py/huckle.svg
.. _pypi: https://badge.fury.io/py/huckle
