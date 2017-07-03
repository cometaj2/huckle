from __future__ import absolute_import, division, print_function

import subprocess
import os

def test_function():
    cmd1 = 'tests/test_huckle_pull.sh'
    p1 = subprocess.Popen(cmd1.split(), stdout=subprocess.PIPE)
    out, err = p1.communicate(str.encode('utf-8'))

    assert('{\n  "hello": "world"\n}'.encode('utf-8') in out)
