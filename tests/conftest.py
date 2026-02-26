import subprocess
import os
import pytest

# bootstrap the test by starting an hcli server with mgmt config and fresh * admin creds
@pytest.fixture(scope="module")
def gunicorn_server_auth():
    # Start gunicorn server
    setup = """
    #!/bin/bash
    set -x
    export NOTIFY_SOCKET=

    rm -rf ~/.huckle_test
    mkdir ~/.huckle_test
    rm -rf ~/.hcli_core_test
    mkdir ~/.hcli_core_test
    export HCLI_CORE_HOME_TEST=$HCLI_CORE_HOME
    export HCLI_CORE_HOME=~/.hcli_core_test
    export HUCKLE_HOME_TEST=$HUCKLE_HOME
    export HUCKLE_HOME=~/.huckle_test
    export HCLI_CORE_BOOTSTRAP_PASSWORD=yehaw
    eval $(huckle env)

    echo "Cleanup preexisting huckle hcli installations..."
    huckle cli rm hco
    huckle cli rm jsonf
    huckle cli rm hfm

    echo "Cleanup old run data..."
    rm -f ./gunicorn-error.log

    hcli_core cli install `hcli_core sample jsonf`
    hcli_core cli config jsonf core.port 18080
    hcli_core cli config jsonf core.auth True
    hcli_core cli config jsonf hco.port 19090
    hcli_core cli config jsonf hco.credentials local

    echo "$(hcli_core cli run jsonf) --daemon --log-file=./gunicorn.log --error-logfile=./gunicorn-error.log --capture-output" | bash

    sleep 2

    echo "Checking port status..."
    netstat -tuln | grep 18080 || echo "Port 18080 not listening"
    netstat -tuln | grep 19090 || echo "Port 19090 not listening"
    ps aux | grep '[g]unicorn' || echo "No gunicorn processes found"
    cat ./gunicorn-error.log
    cat ./gunicorn.log

    huckle cli install http://127.0.0.1:18080
    huckle cli install http://127.0.0.1:19090

    echo "Setup bootstrap admin config and credentials for hco and jsonf..."
    huckle cli config jsonf credential.helper keyring
    huckle cli config hco credential.helper keyring
    huckle cli credential hco admin <<< $HCLI_CORE_BOOTSTRAP_PASSWORD
    huckle cli credential jsonf admin <<< $HCLI_CORE_BOOTSTRAP_PASSWORD

    huckle cli config jsonf credential.helper huckle
    huckle cli config hco credential.helper huckle
    huckle cli credential hco admin <<< $HCLI_CORE_BOOTSTRAP_PASSWORD
    huckle cli credential jsonf admin <<< $HCLI_CORE_BOOTSTRAP_PASSWORD

    echo "Setting up basic auth config..."
    huckle cli config hco auth.mode basic
    huckle cli config jsonf auth.mode basic

    """
    process = subprocess.Popen(['bash', '-c', setup], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()

    result = out.decode('utf-8')
    error = err.decode('utf-8')

    print(result)
    print(error)

    # Verify setup worked
    assert os.path.exists('./gunicorn-error.log'), "gunicorn-error.log not found"

# bootstrap the test by starting an hcli server with mgmt config and fresh * admin creds
@pytest.fixture(scope="module")
def gunicorn_server_remote_auth():
    # Start gunicorn server
    setup = """
    #!/bin/bash
    set -x
    export NOTIFY_SOCKET=

    rm -rf ~/.remote_huckle_test
    mkdir ~/.remote_huckle_test
    rm -rf ~/.hcli_core_test
    mkdir ~/.hcli_core_test
    export HCLI_CORE_HOME=~/.hcli_core_test
    export HUCKLE_HOME=~/.remote_huckle_test
    export HCLI_CORE_BOOTSTRAP_PASSWORD=yehaw
    eval $(huckle env)

    echo "Cleanup preexisting huckle hcli installations..."
    huckle cli rm hco
    huckle cli rm jsonf
    huckle cli rm hfm

    echo "Cleanup old run data..."
    rm -f ./remote_hco_gunicorn-error.log
    rm -f ./remote_gunicorn-error.log

    hcli_core cli install `hcli_core path`/cli
    hcli_core cli config jsonf --unset core.port
    hcli_core cli config jsonf core.auth True
    hcli_core cli config jsonf hco.port 29000
    hcli_core cli config jsonf hco.credentials local

    echo "$(hcli_core cli run jsonf) --daemon --log-file=./remote_hco_gunicorn.log --error-logfile=./remote_hco_gunicorn-error.log --capture-output" | bash

    export HCLI_CORE_HOME=~/.hcli_core_remote_test
    hcli_core cli install `hcli_core path`/cli
    hcli_core cli config jsonf core.port 28000
    hcli_core cli config jsonf core.auth True
    hcli_core cli config jsonf --unset hco.port
    hcli_core cli config jsonf hco.credentials remote

    echo "$(hcli_core cli run jsonf) --daemon --log-file=./remote_gunicorn.log --error-logfile=./remote_gunicorn-error.log --capture-output" | bash

    sleep 2

    huckle cli install http://127.0.0.1:28000
    huckle cli install http://127.0.0.1:29000

    echo "Setup bootstrap admin config and credentials for hco and jsonf..."
    huckle cli credential hco admin <<< $HCLI_CORE_BOOTSTRAP_PASSWORD
    huckle cli credential jsonf admin <<< $HCLI_CORE_BOOTSTRAP_PASSWORD

    echo "Setting up basic auth config..."
    huckle cli config hco auth.mode basic
    huckle cli config jsonf auth.mode basic

    """
    process = subprocess.Popen(['bash', '-c', setup], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    out, err = process.communicate()

    # Verify setup worked
    assert os.path.exists('./remote_hco_gunicorn-error.log'), "remote_hco_gunicorn-error.log not found"
    assert os.path.exists('./remote_gunicorn-error.log'), "remote_gunicorn-error.log not found"

@pytest.fixture(scope="module")
def cleanup():

    # Let the tests run
    yield

    # Enhanced cleanup with verification
    cleanup_script = """
    #!/bin/bash
    set -x
    export NOTIFY_SOCKET=

    rm -rf ~/.huckle_test
    rm -rf ~/.remote_huckle_test
    rm -rf ~/.hcli_core_test
    rm -rf ~/.hcli_core_remote_test
    export HUCKLE_HOME=$HUCKLE_HOME_TEST
    export HCLI_CORE_HOME=$HCLI_CORE_HOME_TEST

    # Force kill any remaining processes

    #ps aux | grep '[g]unicorn' | awk '{print $2}' | xargs pkill -9 -f
    pkill -9 -f 'gunicorn.*hcli_core:connector'
    """

    # Run cleanup and capture output
    cleanup_process = subprocess.run(['bash', '-c', cleanup_script], capture_output=True, text=True)

    # One final check with Python's os module
    if os.path.exists('./gunicorn-error.log'):
        os.remove('./gunicorn-error.log')
    if os.path.exists('./gunicorn-noauth-error.log'):
        os.remove('./gunicorn-noauth-error.log')
    if os.path.exists('./test_config'):
        os.remove('./test_config')
    if os.path.exists('./noauth_config'):
        os.remove('./noauth_config')
    if os.path.exists('./test_config.lock'):
        os.remove('./test_config.lock')
    if os.path.exists('./noauth_config.lock'):
        os.remove('./noauth_config.lock')
    if os.path.exists('./remote_hco_gunicorn-error.log'):
        os.remove('./remote_hco_gunicorn-error.log')
    if os.path.exists('./remote_gunicorn-error.log'):
        os.remove('./remote_gunicorn-error.log')
    if os.path.exists('./remote_hco_test_config'):
        os.remove('./remote_hco_test_config')
    if os.path.exists('./remote_test_config'):
        os.remove('./remote_test_config')
    if os.path.exists('./remote_hco_test_config.lock'):
        os.remove('./remote_hco_test_config.lock')
    if os.path.exists('./remote_test_config.lock'):
        os.remove('./remote_test_config.lock')
    if os.path.exists('./credentials'):
        os.remove('./credentials')
    if os.path.exists('./credentials.lock'):
        os.remove('./credentials.lock')

    # Verify files are gone
    assert not os.path.exists('./gunicorn-error.log'), "gunicorn-error.log still exists"
    assert not os.path.exists('./gunicorn-noauth-error.log'), "gunicorn-noauth-error.log still exists"
    assert not os.path.exists('./test_config'), "test_config still exists"
    assert not os.path.exists('./test_config.lock'), "test_config.lock still exists"
    assert not os.path.exists('./noauth_config'), "test_config still exists"
    assert not os.path.exists('./noauth_config.lock'), "noauth_config.lock file still exists"
    assert not os.path.exists('./remote_hco_gunicorn-error.log'), "gunicorn-error.log still exists"
    assert not os.path.exists('./remote_gunicorn-error.log'), "gunicorn-error.log still exists"
    assert not os.path.exists('./remote_hco_test_config'), "remote_hco_test_config still exists"
    assert not os.path.exists('./remote_hco_test_config.lock'), "remote_hco_test_config.lock still exists"
    assert not os.path.exists('./remote_test_config'), "remote_test_config still exists"
    assert not os.path.exists('./remote_test_config.lock'), "remote_test_config.lock still exists"
    assert not os.path.exists('./credentials'), "credentials still exists"
    assert not os.path.exists('./credentials.lock'), "credentials.lock still exists"
