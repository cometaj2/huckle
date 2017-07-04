from __future__ import absolute_import, division, print_function

import subprocess
import os

def test_function():
    out = subprocess.check_output(['./tests/test_huckle_pull.sh'])

    assert('{\n  "hello": "world"\n}' in out)
