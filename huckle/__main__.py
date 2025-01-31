import sys
import traceback

from contextlib import nullcontext

from huckle import config
from huckle import huckle
from huckle import stdin
from huckle import logger

logging = logger.Logger()

# helps with printing error messages to STDERR
def eprint(*args, **kwargs):
#     print(*args, file=sys.stderr, **kwargs)
    # Join args with spaces and write directly
    msg = ' '.join(str(arg) for arg in args)
    sys.stderr.write(msg)

# prototype generator to identity generators as a type
def generator():
    yield

def main():

    # Only handle and consume -n for huckle commands to help work around terminal aesthetics
    no_newline = False
    if len(sys.argv) > 0 and (sys.argv[0] == "huckle" or 
        (len(sys.argv) > 1 and sys.argv[0].endswith("huckle"))):
        if '-n' in sys.argv:
            no_newline = True
            sys.argv.remove('-n')

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
            dest = None
            stdout_bytes_written = 0
            stderr_bytes_written = 0
            for dest, chunk in output:  # Now unpacking tuple of (dest, chunk)
                stream = sys.stderr if dest == 'stderr' else sys.stdout
                f = getattr(stream, 'buffer', stream)
                if chunk:
                    f.write(chunk)
                    f.flush()

                    # Track total bytes written to each stream
                    if dest == 'stdout':
                        stdout_bytes_written += len(chunk)
                    else:
                        stderr_bytes_written += len(chunk)

                    if dest == 'stderr':
                        try:
                            error = chunk.decode('utf-8')
                            logging.error(error)
                        except UnicodeDecodeError:
                            eprint(chunk)
                            logging.error(chunk)

                        # Add newline for stderr before exit if needed
                        if stderr_bytes_written > 0 and not no_newline:
                            sys.stderr.write('\n')
                        sys.exit(1)

            # Add newlines after all output so that other *nix tools will work correctly
            if not no_newline:
                if dest == 'stdout' and stdout_bytes_written > 0:
                    sys.stdout.write('\n')
                elif dest == 'stderr' and sterr_bytes_written > 0:
                    eprint('\n')
        else:
            error = "huckle: unexpected non-generator type."
            eprint(error)
            logging.error(error)
            logging.error(type(output))
            logging.error(output)
            if not no_newline:
                eprint('\n')
    except Exception as error:
        trace = traceback.format_exc()
        eprint(error)
        logging.error(trace)
        if not no_newline:
            eprint('\n')
        sys.exit(1)

