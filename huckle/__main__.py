from __future__ import absolute_import, division, print_function

import sys

from huckle import hutils
from huckle import config
from huckle import huckle
from huckle import logger

logging = logger.Logger()
logging.setLevel(logger.INFO)


# prototype generator to identity generators as a type
def generator():
    yield

def main():
    hutils.create_folder(config.dot_huckle)
    hutils.create_folder(config.dot_huckle_scripts)
    hutils.create_file(config.dot_bash_profile)

    try:
        output = huckle.cli()

        if isinstance(output, str):
            print(output)
        elif isinstance(output, type(generator())):
            f = getattr(sys.stdout, 'buffer', sys.stdout)
            for chunk in output:
                if chunk:
                    f.write(chunk)

            f.flush()
        else:
            pass
    except Exception as error:
        hutils.eprint(error)
