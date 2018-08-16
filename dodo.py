#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import sys
sys.dont_write_bytecode = True

from glob import glob

from doit.task import clean_targets
from cr.utils.fmt import fmt
from cr.utils.git import subs2shas
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

SUBS2SHAS = subs2shas()

try:
    J = call('nproc')[1].strip()
except:
    J = 1

try:
    RMRF = which('rmrf')
except:
    RMRF = 'rm -rf'

def task_submod():
    '''
    run ensure git submodules are up to date
    '''
    SYMS = [
        '+',
        '-',
    ]
    for submod, sha1hash in SUBS2SHAS.items():
        yield dict(
            name=submod,
            actions=[
                fmt('git submodule update --init {submod}')
            ],
            uptodate=[all(map(lambda sym: not sha1hash.startswith(sym), SYMS))],
        )

def pyfiles():
    with cd(REPOROOT):
        return sorted(glob('cr/**/*.py', recursive=True))

def task_pyfiles():
    '''
    list py files
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
        task_dep=[
            'submod',
        ],
        actions=[
            fmt('{PYTHON} -B -m pytest -s -vv {TESTDIR}'),
        ],
    )

def task_pycov():
    '''
    run pycov
    '''
    return dict(
        task_dep=[
            'submod',
        ],
        actions=[
            fmt('pytest {PYTHON} -B -m pytest -s -vv --cov={CRDIR} {TESTDIR}'),
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
