import subprocess
import os
import pytest

def test_hco_key_admin(gunicorn_server_auth, cleanup):
    hello = """
    #!/bin/bash
    set -x

    echo "Wipeout auth to fail..."
    sed -i.backup 's/auth.mode = basic/auth.mode = skip/' ~/.huckle/etc/hco/config

    export PATH=$PATH:~/.huckle/bin
    hco key admin

    """

    p2 = subprocess.Popen(['bash', '-c', hello], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p2.communicate()
    result = out.decode('utf-8')
    error = err.decode('utf-8')

    print(result)
    print(error)

    assert 'no authorization header' in error.lower()

def test_jsonf(gunicorn_server_auth, cleanup):
    hello = """
    #!/bin/bash

    echo "Wipeout auth to fail..."
    sed -i.backup 's/auth.mode = basic/auth.mode = skip/' ~/.huckle/etc/jsonf/config

    export PATH=$PATH:~/.huckle/bin
    echo '{"hello":"world"}' | jsonf go
    kill $(ps aux | grep '[g]unicorn' | awk '{print $2}')
    """

    p2 = subprocess.Popen(['bash', '-c', hello], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p2.communicate()
    result = out.decode('utf-8')
    error = err.decode('utf-8')

    print(result)
    print(error)

    assert 'no authorization header' in error.lower()
