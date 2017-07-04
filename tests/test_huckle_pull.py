from __future__ import absolute_import, division, print_function

import subprocess
import os

def test_function():
    script = """
    #!/bin/bash

    shopt -s expand_aliases
    huckle pull https://hcli.io/hcli-webapp/cli/jsonf?command=jsonf
    . ~/.huckle/huckle_profile
    echo {"hello":"world"} | jsonf go
    """

    p1 = subprocess.Popen(['bash', '-c', script], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    out, err = p1.communicate()
    result = out.decode('utf-8')

    assert('{\n  "hello": "world"\n}' in result)
