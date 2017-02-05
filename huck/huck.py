import sys

def navigate(argv):
    if len(sys.argv) > 1:
        for x in sys.argv[1:]:
            print('Hello %s!' % x)
