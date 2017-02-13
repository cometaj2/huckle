import os
import sys

from setuptools import setup, find_packages
from codecs import open
from os import path
from huckle import config

#import subprocess, re
#from distutils.command.sdist import sdist as _sdist
#from distutils.core import setup, Command

#VERSION_PY = """
# This file is originally generated from Git information by running 'setup.py
# version'. Distribution tarballs contain a pre-generated copy of this file.
#
#__version__ = '%s'
#"""
#def update_version_py():
#    if not os.path.isdir(".git"):
#        print "This does not appear to be a Git repository."
#        return
#    try:
#        p = subprocess.Popen(["git", "describe",
#                              "--tags", "--dirty", "--always"],
#                             stdout=subprocess.PIPE)
#    except EnvironmentError:
#        print "unable to run git, leaving huckle/version.py alone"
#        return
#    stdout = p.communicate()[0]
#    if p.returncode != 0:
#        print "unable to run git, leaving huckle/version.py alone"
#        return
#
#    # we use tags like "huckle-0.1.0.dev1", so strip the prefix
#    #assert stdout.startswith("huckle-")
#    ver = stdout[len("huckle-"):].strip()
#    f = open("huckle/version.py", "w")
#    f.write(VERSION_PY % ver)
#    f.close()
#    print "set huckle/version.py to '%s'" % ver

#def get_version():
#    try:
#        f = open("huckle/_version.py")
#    except EnvironmentError:
#        return None
#    for line in f.readlines():
#        mo = re.match("__version__ = '([^']+)'", line)
#        if mo:
#            ver = mo.group(1)
#            return ver
#    return None

if sys.argv[-1] == 'publish':
    os.system("rm -rf dist")
    os.system("python setup.py sdist")
    os.system("twine upload dist/* -r pypi")
    os.system("git tag -a %s -m 'version %s'" % ("huckle-" + config.__version__, "huckle-" + config.__version__))
    sys.exit()

if sys.argv[-1] == 'tag':
    os.system("git tag -a %s -m 'version %s'" % ("huckle-" + config.__version__, "huckle-" + config.__version__))
    sys.exit()

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='huckle',
    version=config.__version__,
    description='A generic CLI that can be used with any API that abides by the standard hypertext command line interface (HCLI) semantics.',
    long_description=long_description,
    url='https://github.com/cometaj2/huckle',
    author='Jeff Michaud',
    author_email='cometaj2@comcast.net',
    license='MIT',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: User Interfaces',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='cli client hypermedia rest generic development',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=[config.dependencies[0]],
    entry_points={
        'console_scripts': [
            'huckle=huckle.__main__:main',
        ],
    },
)
