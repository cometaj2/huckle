import sys

from huckle import hutils
from huckle import config
from huckle import huckle

# prototype generator to identity generators as a type
def generator():
    yield

def main():
    try:
        output = huckle.cli()
        if isinstance(output, str):
            print(output)
        elif isinstance(output, type(generator())):
            for dest, chunk in output:  # Now unpacking tuple of (dest, chunk)
                stream = sys.stderr if dest == 'stderr' else sys.stdout
                f = getattr(stream, 'buffer', stream)
                if chunk:
                    f.write(chunk)
                f.flush()
                if dest == 'stderr':
                    sys.exit(1)
        else:
            pass
    except Exception as error:
        hutils.eprint(error)
        sys.exit(1)
