Huck (hypermedia unified CLI... with a "k")
===========================================

Huck is a very specific form of generic hypermedia client that plays in the
command line interface (CLI) space. It's a CLI that understands any hypermedia
API (REST API) that abide by a specific hypermedia API CLI pattern.

----

As is normally seen with any hypermedia client under REST, all changes published
by the server are instantaneously distributed to all clients without there being
a need to update the client as the API changes. This is used to huck's advantage
and brings these benefits to the shell command line.

Once a CLI is created via huck, it can be invoked by name directly. Huck then takes
over and provides a dynamic view of the documentation and commands that can be issued
to the CLI API it's associated to.

Usage
-----

huck create [cliname]

    This aliases a new cliname for use via huck. The current implementation simply leverages
    .bash_profile aliases.

huck cli [cliname]

    Invokes the cliname to issue API calls, the details of which are left to API implementers.
    
    Documentation and commands are presented gradually, as incomplete calls are made, to provide
    users with a way to incrementally discover and learn how calls are issued to an API.

Configuration
-------------

Huck uses the .bash_profile to defer to a ~/.huck/huck_profile for CLI aliases; to avoid
crowding the .bash_profile and to facilitate cleanup if huck is uninstalled.

Huck also uses CLI configuration files (e.g. ~/.huck/usp5/config) to associate a specific
CLI, usp5 in this example, to a hypermedia API url root.

Each CLI configuration file contains:
    - A URL to the root of the hypermedia CLI API

