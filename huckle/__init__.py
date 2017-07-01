from __future__ import absolute_import

from .huckle import hutils
from .huckle import config

hutils.create_folder(config.dot_huckle)
hutils.create_file(config.dot_huckle_profile)
hutils.create_file(config.dot_bash_profile)
