Huck (hypermedia unified cli... with a "k"
==========================================

Huck is a very specific form of generic hypermedia client. It impersonates
a command line interface (CLI) application that instantly provides a CLI to
*any* hypermedia API (REST API) that follows the standard hypermedia CLI
pattern.

----

As is normally seen with any hypermedia client under REST, all changes published
by the server are instantaneously distributed to all huck clients without
there being a need to update the CLI client as the API changes. This is used to
huck's advantage.

Huck uses profiles (e.g. profile_aws), stored under ~./huck to associate a
specific CLI to a hypermedia API that abides by the standard hypermedia CLI
pattern.

Each profile contains two things:
    - A URL to the root of the hypermedia API
    - A CLI name

Once a profile is created, the CLI can then be invoked by name. Huck takes
over and provides a dynamic view of the commands and documentation
that can be used to issue CLI calls to the API it's associated to.
