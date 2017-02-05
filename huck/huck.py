import sys
import json
from haleasy import HALEasy

def navigate(argv):
    if len(sys.argv) > 1:
        for x in sys.argv[1:]:
            print('Hello %s!' % x)
            h = HALEasy('http://haltalk.herokuapp.com/')
            print json.dumps(h.properties(), indent=4, sort_keys=True)
