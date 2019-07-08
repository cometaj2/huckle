from __future__ import absolute_import, division, print_function

import subprocess
import os

def test_function():
    setup = """
    #!/bin/bash

    gunicorn --workers=1 --threads=1 --chdir `hcli_core path` "hcli_core:HCLI().connector" --daemon
    huckle cli install http://127.0.0.1:8000
    """

    p1 = subprocess.Popen(['bash', '-c', setup], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    out, err = p1.communicate()

    hello = """
    #!/bin/bash

    export PATH=$PATH:~/.huckle/bin
    echo '{"hello":"world"}' | jsonf go
    """
    
    p2 = subprocess.Popen(['bash', '-c', hello], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    out, err = p2.communicate()
    result = out.decode('utf-8')

    assert('{\n    "hello": "world"\n}\n' in result)
