#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import sys
sys.dont_write_bytecode = True

from glob import glob
from itertools import chain
from setuptools import Command, find_packages, setup

from cr.version import version

SCRIPT_FILE = os.path.abspath(__file__)
SCRIPT_NAME = os.path.basename(SCRIPT_FILE)
SCRIPT_PATH = os.path.dirname(SCRIPT_FILE)
if os.path.islink(__file__):
    REAL_FILE = os.path.abspath(os.readlink(__file__))
    REAL_NAME = os.path.basename(REAL_FILE)
    REAL_PATH = os.path.dirname(REAL_FILE)

NAME, EXT = os.path.splitext(SCRIPT_NAME)

def get_reqs(*paths, recursive=False):
    filepaths = chain(*[glob(os.path.join(SCRIPT_PATH, path, '**/requirements.txt'), recursive=recursive) for path in paths])
    return list(set(chain(*[open(filepath).read().splitlines() for filepath in filepaths])))

INSTALL_REQS = get_reqs('.')

with open(os.path.join(SCRIPT_PATH, 'LICENSE')) as f:
    LICENSE = f.read()

with open(os.path.join(SCRIPT_PATH, 'README.rst')) as f:
    README = f.read()

setup(
    name ='cr-cli',
    version = version[1:] if version.startswith('v') else version,
    description = 'bugzilla cli in Python',
    long_description = README,
    url = 'https://github.com/mozilla-it/cr-cli',
    author = 'Scott Idler',
    author_email = 'sidler@mozilla.com',
    license = LICENSE,
    keywords = 'cli',
    packages = find_packages(exclude=['docs', 'tests*']),
    install_requires = INSTALL_REQS,
    entry_points = dict(console_scripts=['cr=cr.cli:main']),
)

