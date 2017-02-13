# Always prefer setuptools over distutils
from setuptools import setup, find_packages

# To use a consistent encoding
from codecs import open
from os import path

from huckle import config

from distutils.command.sdist import sdist as _sdist

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='huckle',
    version=config.version,
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
