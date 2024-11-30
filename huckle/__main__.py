import sys
import traceback

from contextlib import nullcontext

from huckle import hutils
from huckle import config
from huckle import huckle
from huckle import stdin
from huckle import logger

logging = logger.Logger()


# prototype generator to identity generators as a type
def generator():
    yield

def main():
    try:
        # Read from stdin if there's input available
        input_data = None
        if not sys.stdin.isatty():
            input_data = sys.stdin.buffer.read()

        output = None
        with stdin(input_data) if input_data else nullcontext():
            output = huckle.cli()

        if output is None:
            return

        if isinstance(output, type(generator())):
            for dest, chunk in output:  # Now unpacking tuple of (dest, chunk)
                stream = sys.stderr if dest == 'stderr' else sys.stdout
                f = getattr(stream, 'buffer', stream)
                if chunk:
                    f.write(chunk)
                f.flush()
                if dest == 'stderr':
                    try:
                        error = chunk.decode('utf-8').strip()
                        logging.error(error)
                    except UnicodeDecodeError:
                        logging.error("huckle: unexpected binary stderr output type")
                    sys.exit(1)
        else:
            error = "huckle: unexpected non-generator type."
            hutils.eprint(error)
            logging.error(error)
            logging.error(type(output))
            logging.error(output)
    except Exception as error:
        trace = traceback.format_exc()
        hutils.eprint(error)
        logging.error(trace)
        sys.exit(1)

