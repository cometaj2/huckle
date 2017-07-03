from __future__ import absolute_import, division, print_function

import subprocess
import os

def test_function():
    cmd1 = './test_huckle_pull.sh'
    p1 = subprocess.Popen(cmd1.split(), stdout=subprocess.PIPE)
    out, err = p1.communicate()

    assert '{\n  "hello": "world"\n}' in out
