Huckle (hypermedia unified CLI... with a kick)
============================================

Huckle is a very specific form of generic hypermedia client that plays in the
command line interface (CLI) space. It's a CLI that understands any hypermedia
API (REST API) that abide by a specific hypermedia API CLI pattern.

----

As is normally seen with any well-behaved client/server interaction under REST,
all changes published by the server are distributed to all clients without there
being a need to update the client as the API changes. This is used to huckle's
advantage and this benefit is brought to the shell command line interface.

Huckle provides a dynamic view of the documentation, commands, options and
parameters that can be issued to the HCLI APIs it interacts with.

What can be noticed is that any API implementer, that abides by a specific
hypermedia API CLI pattern, gets a client side shell CLI for their API for free;
and given that most programming languages have a way to issue shell commands, such
APIs become readily consumable anywhere, and can be experimented with quickly
by developers.

The standard hypermedia API CLI pattern definition is a work in progress by the
author with the HCLI Internet-Draft [1]. The current implementation leverages hal+json
alongside a static form of ALPS (semantic profile) [2] to help enable widespread cross
media-type support.

Help shape huckle and HCLI on the discussion list [3] or by raising issues on github!

[1] https://github.com/cometaj2/I-D/tree/master/hcli

[2] http://alps.io/

[2] https://groups.google.com/forum/#!forum/huck-hypermedia-unified-cli-with-a-kick

Usage
-----

huckle create [cliname]

    This creates an new cliname alias and configuration file. Once a CLI is created via huckle,
    it can be invoked by name directly after restarting the terminal.
   
    Note that an existing configuration file is left alone if the command is run multiple times 
    for the same cliname.

huckle cli [cliname]

    This invokes the cliname to issue API calls; the details of which are left to API implementers.
    
    Documentation and commands are presented gradually, as incomplete calls are made, to provide
    users with a way to incrementally discover and learn how CLI calls are issued to an API.

huckle help

    This opens up a man page that describes how to use huckle.

Configuration
-------------

Huckle uses the .bash_profile to defer to a ~/.huckle/huckle_profile for CLI aliases; to avoid
crowding the .bash_profile and to facilitate cleanup if huckle is uninstalled.

Huckle also uses CLI configuration files (e.g. ~/.huckle/<cliname>/config) to associate a specific
CLI to a hypermedia API url root.

Each CLI configuration file contains:
    - A URL to the root of the hypermedia CLI API

Supports
--------

Support automatic man page document when dropping the "help" keyword anywhere in a command line sequence.

Supports HCLI version 1.0 semantics for:

    - hal+json

Supports responses for:

    - application/json

To Do
-----
Support HCLI version 1.0 semantics for: 

    - Collection+JSON
    - hal+xml
    - HTML
    - Siren
    - JSON API
    - JSON-LD
    - Mason

Support streaming application/octet-stream to the server from STDIN
    
Support application/octet-stream media-type response reception

Support for forward proxy configuration  

Support various authentication per CLI configuration  

    - HTTP Basic Auth  
    - HTTP Digest  
    - Oauth  
    - X509 (HTTPS mutual authentication)  
    - SAML  

Support server certificate validation bypass (e.g. --ssl-no-verify. This is not secure but is sometimes useful to troubleshoot)  
