import sys
import config
import json

from haleasy import HALEasy

usage = """Usage:
   
- huck create <cliname> to alias into a new cli. Restarting the terminal
  is required since we're using a .bash_profile alias.
                   
- huck cli <cliname> to invoke a cli. Note that the <cliname> alias created with
  huck create <cliname> should be used instead, for brevity.
"""

def navigate(argv):
    for x in argv:
        h = HALEasy(config.url)
        print json.dumps(h.properties(), indent=4, sort_keys=True)

def cli():
    if len(sys.argv) > 2:
        if sys.argv[1] == "cli":
            config.parse_configuration(sys.argv[2])
            navigate(sys.argv[2:])
        if sys.argv[1] == "create":
            config.alias_cli(sys.argv[2])
    else:
        sys.exit(usage)
