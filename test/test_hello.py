import subprocess
import os

def test_function():
    out = os.popen("echo '{\"hello\":\"world\"}'").read()
    assert "{\"hello\":\"world\"}" in out
