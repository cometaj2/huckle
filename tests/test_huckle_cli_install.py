import subprocess
import os

def test_function():
    setup = """
    #!/bin/bash

    gunicorn --workers=1 --threads=1 "hcli_core:connector()" --daemon
    huckle cli install http://127.0.0.1:8000
    echo '{"hello":"world"}' | jsonf go
    """

    p1 = subprocess.Popen(['bash', '-c', setup], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    out, err = p1.communicate()

    hello = """
    #!/bin/bash

    export PATH=$PATH:~/.huckle/bin
    echo '{"hello":"world"}' | jsonf go
    kill $(ps aux | grep '[g]unicorn' | awk '{print $2}')
    """

    p2 = subprocess.Popen(['bash', '-c', hello], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    out, err = p2.communicate()
    result = out.decode('utf-8')

    assert('{\n    "hello": "world"\n}\n' in result)
