import tomllib
import os
import sys
import subprocess

with open("./pyproject.toml", "rb") as f:
    data = tomllib.load(f)

version = data['project']['version']

if sys.argv[-1] == 'dry-run':
    branch = subprocess.check_output('git rev-parse --abbrev-ref HEAD', shell=True).strip().decode("utf-8")
    if branch != "master":
        sys.exit("dry-run from a branch other than master is disallowed.")
    os.system("rm -rf huckle.egg-info")
    os.system("rm -rf build")
    os.system("rm -rf dist")
    os.system("python -m build --sdist --wheel")
    os.system("twine check dist/*")
    sys.exit()

if sys.argv[-1] == 'publish':
    branch = subprocess.check_output('git rev-parse --abbrev-ref HEAD', shell=True).strip()
    if branch.decode('ASCII') != "master":
        sys.exit("publishing from a branch other than master is disallowed.")
    os.system("rm -rf huckle.egg-info")
    os.system("rm -rf build")
    os.system("rm -rf dist")
    os.system("python -m build --sdist --wheel")
    os.system("twine upload dist/* -r pypi")
    os.system("git tag -a %s -m 'version %s'" % ("huckle-" + version, "huckle-" + version))
    os.system("git push")
    os.system("git push --tags")
    sys.exit()

if sys.argv[-1] == 'tag':
    branch = subprocess.check_output('git rev-parse --abbrev-ref HEAD', shell=True).strip()
    if branch != "master":
        sys.exit("tagging from a branch other than master is disallowed.")
    os.system("git tag -a %s -m 'version %s'" % ("huckle-" + version, "huckle-" + version))
    sys.exit()
