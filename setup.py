from __future__ import absolute_import, division, print_function

import os
import sys
import subprocess

from setuptools import setup, find_packages
from codecs import open
from os import path
from huckle import package
from huckle import hutils

if sys.argv[-1] == 'publish':
    branch = subprocess.check_output('git rev-parse --abbrev-ref HEAD', shell=True).strip()
    if branch != "master":
        sys.exit("publishing from a branch other than master is disallowed.")
    os.system("rm -rf dist")
    os.system("python setup.py sdist")
    os.system("twine upload dist/* -r pypi")
    os.system("git tag -a %s -m 'version %s'" % ("huckle-" + package.__version__, "huckle-" + package.__version__))
    os.system("git push")
    os.system("git push --tags")
    sys.exit()

if sys.argv[-1] == 'tag':
    branch = subprocess.check_output('git rev-parse --abbrev-ref HEAD', shell=True).strip()
    if branch != "master":
        sys.exit("tagging from a branch other than master is disallowed.")
    os.system("git tag -a %s -m 'version %s'" % ("huckle-" + package.__version__, "huckle-" + package.__version__))
    sys.exit()

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='huckle',
    version=package.__version__,
    description='A CLI that can act as an impostor for any CLI expressed through hypertext command line interface (HCLI) semantics.',
    long_description=long_description,
    url='https://github.com/cometaj2/huckle',
    author='Jeff Michaud',
    author_email='cometaj2@comcast.net',
    license='MIT',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='cli client hypermedia rest generic development',
    packages=find_packages(exclude=['__pycache__', 'tests']),
    install_requires=[package.dependencies[0],
                      package.dependencies[1],
                      package.dependencies[2]],
    package_data={'huckle': ['data/*']},
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'huckle=huckle.__main__:main',
        ],
    },
)
