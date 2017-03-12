import os
import sys
import subprocess

from setuptools import setup, find_packages
from codecs import open
from os import path
from huckle import config
from huckle import utils

if sys.argv[-1] == 'publish':
    branch = subprocess.check_output('git rev-parse --abbrev-ref HEAD', shell=True).strip()
    if branch != "master":
        sys.exit("publishing from a branch other than master is disallowed.")
    os.system("rm -rf dist")
    os.system("python setup.py sdist")
    os.system("twine upload dist/* -r pypi")
    os.system("git tag -a %s -m 'version %s'" % ("huckle-" + config.__version__, "huckle-" + config.__version__))
    sys.exit()

if sys.argv[-1] == 'tag':
    branch = subprocess.check_output('git rev-parse --abbrev-ref HEAD', shell=True).strip()
    if branch != "master":
        sys.exit("tagging from a branch other than master is disallowed.")
    os.system("git tag -a %s -m 'version %s'" % ("huckle-" + config.__version__, "huckle-" + config.__version__))
    sys.exit()

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='huckle',
    version=config.__version__,
    description='A CLI that can act as an impostor for any CLI expressed through hypertext command line interface (HCLI) semantics.',
    long_description=long_description,
    url='https://github.com/cometaj2/huckle',
    author='Jeff Michaud',
    author_email='cometaj2@comcast.net',
    license='MIT',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: User Interfaces',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='cli client hypermedia rest generic development',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=[config.dependencies[0],
                      config.dependencies[1]],
    package_data={
        'huckle': ['data/huckle.man'],
    },
    entry_points={
        'console_scripts': [
            'huckle=huckle.__main__:main',
        ],
    },
)
