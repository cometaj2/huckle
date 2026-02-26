import subprocess
import os
import pytest

def test_hfm_cp(cleanup):
    setup = """
    #!/bin/bash
    set -x
    export NOTIFY_SOCKET=

    export HCLI_CORE_HOME=~/.hcli_core_test
    export HUCKLE_HOME=~/.huckle_test
    eval $(huckle env)

    hcli_core cli install `hcli_core sample hfm`
    hcli_core cli config hfm core.port 18000
    hcli_core cli config hfm core.auth False

    echo "$(hcli_core cli run hfm) --daemon --log-file=./gunicorn-noauth.log --error-logfile=./gunicorn-noauth-error.log --capture-output" | bash

    cat ./gunicorn-noauth.log
    cat ./gunicorn-noauth-error.log

    huckle cli install http://127.0.0.1:18000
    """

    p1 = subprocess.Popen(['bash', '-c', setup], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p1.communicate()

    if out is not None:
        print(f"STDOUT: {out}")

    if err is not None:
        print(f"STDERR: {err}")

    hello = """
    #!/bin/bash
    set -x

    export HUCKLE_HOME=~/.huckle_test
    eval $(huckle env)
    echo -n '{"hello":"world"}' > hello.json
    cat hello.json | hfm cp -l ./hello.json
    hfm cp -r hello.json > hello1.json
    cat hello1.json
    rm hello.json
    rm hello1.json
    """

    p2 = subprocess.Popen(['bash', '-c', hello], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p2.communicate()
    result = out.decode('utf-8')
    error = err.decode('utf-8')

    if err is not None:
        print(f"STDERR: {err}")

    assert('{"hello":"world"}\n' == result)

