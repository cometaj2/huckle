import sys

# helps with printing error messages to STDERR
def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
