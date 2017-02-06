import sys
import config
import json

from haleasy import HALEasy

def navigate(argv):
    for x in argv:
        h = HALEasy(config.url)
        print json.dumps(h.properties(), indent=4, sort_keys=True)

def cli():
    if len(sys.argv) > 2:
        if sys.argv[1] == "--cli":
            config.parse_configuration(sys.argv[2])
            navigate(sys.argv[2:])
    else:
        sys.exit("Usage: huck --cli <cliname>")
