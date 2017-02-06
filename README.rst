Huck (hypermedia unified CLI... with a "k")
===========================================

Huck is a very specific form of generic hypermedia client that plays in the
CLI space. It's a command line interface (CLI) that impersonates the CLI
of any hypermedia API (REST API) that follows the
standard hypermedia CLI pattern.

----

As is normally seen with any hypermedia client under REST, all changes published
by the server are instantaneously distributed to all clients without there being
a need to update the CLI client as the API changes. This is used to huck's advantage.

Huck uses a CLI configuration files (e.g. ~/.huck/profile_aws) to associate a
specific CLI to a hypermedia API url root and CLI name.

Each cli configuration file contains two things:
    - A URL to the root of the hypermedia API
    - A CLI name

Once a CLI is created, the CLI can then be invoked by name. Huck then takes
over and provides a dynamic view of the commands and documentation that can
be used to issue CLI calls to the API it's associated to.

Usage
=====

huck create <cliname>

    This aliases a new cliname for use via huck. The current implementation simply leverages
    .bash_profile aliases.

huck cli <cliname>

    Invokes the cli name to issue API calls. The details are left to API implementers.
    
    documentation and commands are presented gradually, as incomplete calls are made, to provide
    users with a way to incrementally discover and learn how calls are issued.
