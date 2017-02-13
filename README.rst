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

Huckle provides a dynamic view of the documentation and commands that can be issued
to the CLI APIs it's associated to.

What can be noticed is that any API implementer, that abides by a specific
hypermedia API CLI pattern, gets a client side shell CLI for their API for free;
and given that most programming languages have a way to issue shell commands, such
APIs become readily consumable anywhere, and can be experimented with quickly
by developers.

The standard hypermedia API CLI pattern definition is a work in progress by the
author with the HCLI Internet-Draft [1]. A few candidates are being considered:

    - Media-type specific structure
    - Microformat (http://microformats.org/)
    - ALPS (http://alps.io/)

The current implementation of huckle leverage hal+json with a specific json structure,
but ALPS seems the most likely candidate to help enable widespread cross media-type
support.

Help shape huckle and HCLI on the discussion list [2] or by raising issues on github!

[1] https://github.com/cometaj2/I-D/tree/master/hcli

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

Configuration
-------------

Huckle uses the .bash_profile to defer to a ~/.huckle/huckle_profile for CLI aliases; to avoid
crowding the .bash_profile and to facilitate cleanup if huckle is uninstalled.

Huckle also uses CLI configuration files (e.g. ~/.huckle/<cliname>/config) to associate a specific
CLI to a hypermedia API url root.

Each CLI configuration file contains:
    - A URL to the root of the hypermedia CLI API
