Huck (hypermedia unified CLI... with a kick)
============================================

Huck is a very specific form of generic hypermedia client that plays in the
command line interface (CLI) space. It's a CLI that understands any hypermedia
API (REST API) that abide by a specific hypermedia API CLI pattern.

----

As is normally seen with any hypermedia client under REST, all changes published
by the server are instantaneously distributed to all clients without there being
a need to update the client as the API changes. This is used to huck's advantage
and brings these benefits to the shell command line.

Huck provides a dynamic view of the documentation and commands that can be issued
to the CLI API it's associated to.

Usage
-----

huck create [cliname]

    This creates an new cliname alias and configuration file. Once a CLI is created via huck,
    it can be invoked by name directly after restarting the terminal.
   
    Note that an existing configuration file is left alone if the command is run multiple times 
    for the same cliname.

huck cli [cliname]

    This invokes the cliname to issue API calls; the details of which are left to API implementers.
    
    Documentation and commands are presented gradually, as incomplete calls are made, to provide
    users with a way to incrementally discover and learn how CLI calls are issued to an API.

Configuration
-------------

Huck uses the .bash_profile to defer to a ~/.huck/huck_profile for CLI aliases; to avoid
crowding the .bash_profile and to facilitate cleanup if huck is uninstalled.

Huck also uses CLI configuration files (e.g. ~/.huck/<cliname>/config) to associate a specific
CLI to a hypermedia API url root.

Each CLI configuration file contains:
    - A URL to the root of the hypermedia CLI API
