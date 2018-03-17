from __future__ import absolute_import, division, print_function

from subprocess import check_output
import os

def test_function():
    setup = """
    #!/bin/bash

    huckle install https://hcli.io/hcli/cli/jsonf?command=jsonf
    echo '{"hello":"world"}' | jsonf go
    """

    out = check_output(['bash', '-c', setup])

    hello = """
    #!/bin/bash

    export PATH=$PATH:~/.huckle/bin
    echo '{"hello":"world"}' | jsonf go
    """
    
    out = check_output(['bash', '-c', hello])

    assert('{\n  "hello" : "world"\n}\n' in out)
