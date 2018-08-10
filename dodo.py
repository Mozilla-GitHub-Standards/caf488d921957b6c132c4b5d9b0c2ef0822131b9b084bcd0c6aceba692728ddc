#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import sys
sys.dont_write_bytecode = True

from glob import glob

from doit.task import clean_targets
from cr.utils.fmt import fmt
from cr.utils.shell import cd, call, rglob, globs, which

DOIT_CONFIG = {
    'verbosity': 2,
    'default_tasks': ['test'],
}

DODO = 'dodo.py'
PYTHON = which('python3')
REPOROOT = os.path.dirname(os.path.abspath(__file__))
CRDIR = fmt('{REPOROOT}/cr')
TESTDIR = fmt('{REPOROOT}/tests')
BINDIR = fmt('{REPOROOT}/bin')

try:
    J = call('nproc')[1].strip()
except:
    J = 1

try:
    RMRF = which('rmrf')
except:
    RMRF = 'rm -rf'

def pyfiles():
    with cd(CRDIR):
        return sorted(glob('**/*.py', recursive=True))

def task_list_pyfiles():
    '''
    print all of the pyfiles
    '''
    text = '\n'.join(pyfiles())
    return dict(
        actions=[
            fmt('echo "{text}"'),
        ],
    )

def task_pylint():
    '''
    run pylint
    '''
    for pyfile in pyfiles():
        yield dict(
            name=pyfile,
            actions=[
                fmt('pylint -j{J} --rcfile {TESTDIR}/pylint.rc {pyfile}'),
            ],
        )

def task_pytest():
    '''
    run pytest
    '''
    return dict(
        actions=[
            fmt('{PYTHON} -m pytest -s -vv {TESTDIR}'),
        ],
    )

def task_pycov():
    '''
    run pycov
    '''
    return dict(
        actions=[
            fmt('pytest {PYTHON} -m pytest -s -vv --cov={CRDIR} {TESTDIR}'),
        ],
    )

def task_test():
    '''
    run: pylint, pytest, pycov
    '''
    return dict(
        task_dep=[
            'pylint',
            'pytest',
            'pycov',
        ],
        actions=[
            'echo "testing complete"',
        ],
    )

def task_rmcache():
    '''
    remove pycache files
    '''
    cachedirs = rglob('**/__pycache__')
    print('cachedirs =', cachedirs)
    return dict(
        actions=[
            fmt('{RMRF} **/__pycache__'),
        ],
    )
