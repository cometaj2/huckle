from __future__ import absolute_import, division, print_function

from . import hutils
from . import config
from . import huckle
from . import logger

logging = logger.Logger()
logging.setLevel(logger.INFO)


def main():
    hutils.create_folder(config.dot_huckle)
    hutils.create_folder(config.dot_huckle_scripts)
    hutils.create_file(config.dot_bash_profile)

    huckle.cli()
