Huckle (hypermedia unified CLI... with a kick) |build status|_ |pypi|_ 
============================================

Huckle is a CLI that can act as an impostor for any CLI expressed via hypertext
command line interface (HCLI) semantics.

----

Huckle provides a way for developers to interact with, or script around, any API that exposes HCLI
semantics, while providing dynamic and up to date in-band access to all the API/CLI documentation,
man page style, which showcases commands, options, and parameters avaialable for execution.

Most, if not all, programming languages have a way to issue shell commands. With the help
of a generic HCLI client such as Huckle, APIs that make use of HCLI semantics are readily consumable
anywhere via the familiar CLI mode of operation, and this, without there being a need to write
a custom and dedicated CLI to interact with a specific API.

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

huckle install \<url>

    This attempts to auto create and configure a CLI name if provided with the root URL of an HCLI API.
    If successful, the CLI can be invoked by name, after restarting the terminal.
    
    Note that an existing configuration file is left alone if the command is run multiple times 
    for the same CLI.

    An example CLI that can be used with Huckle is available on hcli.io:
        - https://hcli.io/hcli-webapp/cli/jsonf?command=jsonf (HCLI root)  
        - https://hcli.io/hal/#/hcli-webapp/ (HAL Browser navigation)  

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

This project makes use of semantic versioning (http://semver.org) and may make use of the "devx",
"prealphax", "alphax" "betax", and "rcx" extensions where x is a number (e.g. 0.3.0-prealpha1)
on github. Only full major.minor.patch releases will be pushed to pip from now on.

Supports
--------

- HCLI version 1.0 semantics for:

    - hal+json

- Automatic man page generation with the "help" command, anywhere in a CLI.

- Command line execution responses for

    - All media types

- Streaming:
 
    - Handles very large stdin/stdout streams (fixed chunk size of 16834)

- Error output to stderr on client response status code >= 400

- SOCKS tunneling through environment variables (ALL_PROXY)

- Auto configuration of an HCLI when provided with a url to an HCLI root (e.g. huckle install https://hcli.io/hcli-webapp/cli/jsonf?command=jsonf)  

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

- Better implementation for huckle params/options handling

- Support for re-aliasing a CLI with additional huckle options (e.g. adding "--ssl-no-verify" to huckle cli jsonf's shell script)

- Support server certificate validation bypass (e.g. --ssl-no-verify. This is not secure but is sometimes useful to troubleshoot)  

- Support for viewing information about an HCLI root (e.g. huckle view https://hcli.io/hcli-webapp/cli/jsonf?command=jsonf)

- Support forward proxy configuration through proxy environment variables (HTTP_PROXY, HTTPS_PROXY)

- Support listing of configured CLIs (e.g huckle list)

- Support removal of a configured CLI for the currently selected namespace (e.g. huckle rm jsonf)

- Support hcli name conflic resolution (use namespaces?)
  
    - View currently selected namespace (e.g. huckle ns)
    - Viewing namespace list (e.g. huckle ns list)
    - Selecting a namespace (e.g. huckle ns use abc)
    - Remove an entire namespace and all associated CLIs (e.g. huckle ns rm abc)

- Support multipart/form-data for very large uploads (see requests-toolbelt)

Bugs
----

- There's an edge case that's not covered; when executing a cli by invoking the root of the HCLI only. And more specifically when the root is
not valid HCLI when initially fetching the HALNavigator.

- Carriage return characters "\n" in json don't get converted to line breaks in man pages.  
  
.. |build status| image:: https://travis-ci.org/cometaj2/huckle.svg?branch=master
.. _build status: https://travis-ci.org/cometaj2/huckle
.. |pypi| image:: https://badge.fury.io/py/huckle.svg
.. _pypi: https://badge.fury.io/py/huckle
