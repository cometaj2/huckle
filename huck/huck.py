import sys
import config
import json

from restnavigator import Navigator

usage = """Usage:
   
- huck create <cliname> to alias into a new cli. Restarting the terminal
  is required since we're using a .bash_profile alias.
                   
- huck cli <cliname> to invoke a cli. Note that the <cliname> alias created with
  huck create <cliname> should be used instead, for brevity.
"""

def navigate(argv):
    h = Navigator.hal(config.url, apiname=config.cliname)

    if len(argv) == 1:
      print json.dumps(h(), indent=4, sort_keys=True)

    length = len(argv[1:])
    for i, x in enumerate(argv[1:]):
        try:
            h.links["command"].get_by("name", x)
        except:
            print "ERROR: The \"" + x + "\" command is not available."
            break

        if i == length - 1:
          print json.dumps(h(), indent=4, sort_keys=True)

def cli():
    if len(sys.argv) > 2:
        if sys.argv[1] == "cli":
            config.parse_configuration(sys.argv[2])
            navigate(sys.argv[2:])
        if sys.argv[1] == "create":
            config.create_configuration(sys.argv[2])
            config.alias_cli(sys.argv[2])
    else:
 
        sys.exit(usage)
