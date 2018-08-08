#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import sys
sys.dont_write_bytecode = True

from json import dumps

SCRIPT_FILE = os.path.abspath(__file__)
SCRIPT_NAME = os.path.basename(SCRIPT_FILE)
SCRIPT_PATH = os.path.dirname(SCRIPT_FILE)
if os.path.islink(__file__):
    REAL_FILE = os.path.abspath(os.readlink(__file__))
    REAL_NAME = os.path.basename(REAL_FILE)
    REAL_PATH = os.path.dirname(REAL_FILE)

NAME, EXT = os.path.splitext(SCRIPT_NAME)

from pprint import pprint
from ruamel import yaml
from argparse import ArgumentParser, RawDescriptionHelpFormatter

from cr import ChangeRequest
from cr import add_argument

def defaults_load(filepath, throw=False):
    try:
        return yaml.safe_load(open(filepath))
    except (TypeError, FileNotFoundError) as er:
        if throw:
            raise er
        return {}

class Required(object):
    __instance = None
    def __new__(cls):
        if Required.__instance is None:
            Required.__instance = object.__new__(cls)
        return Required.__instance
    def __repr__(self):
        return 'Required'

class MissingRequiredArgsError(Exception):
    def __init__(self, required_args):
        msg = 'missing required args error:\n' + '\n'.join(sorted(required_args))
        super(MissingRequiredArgsError, self).__init__(msg)

def add_create(subparsers, defaults):
    parser = subparsers.add_parser('create')

    required_group = parser.add_argument_group(title='questionnaire required')
    add_argument(required_group, '-S', '--planned-start-date', default=Required())
    add_argument(required_group, '-E', '--planned-end-date', default=Required())
    add_argument(required_group, '-C', '--change-plan', default=Required())
    add_argument(required_group, '-D', '--short-description', default=Required())
    add_argument(required_group, '-B', '--business-impact', default=Required())
    add_argument(required_group, '-I', '--change-impact', default=Required())

    optional_group = parser.add_argument_group(title='questionnaire optional')
    add_argument(optional_group, '-u', '--user-impact')
    add_argument(optional_group, '-s', '--security-risk-level')
    add_argument(optional_group, '-f', '--change-frequency')
    add_argument(optional_group, '-t', '--test-plan')
    add_argument(optional_group, '-p', '--post-implementation-plan')
    add_argument(optional_group, '-e', '--customer-end-user-plan')
    add_argument(optional_group, '-r', '--rollback-procedure')
    add_argument(optional_group, '-R', '--peer-review-date')
    add_argument(optional_group, '-v', '--vendor-name')
    add_argument(optional_group, '-d', '--planned-downtime')

    parser.set_defaults(**defaults)
    return parser

def add_show(subparsers, defaults):
    parser = subparsers.add_parser('show')
    parser.add_argument(
        '--show-arg1',
        help='show arg1')
    parser.add_argument(
        '--show-arg2',
        help='show arg2')

    parser.set_defaults(**defaults)
    return parser

def validate(**kwargs):
    required_args = [arg for arg, value in kwargs.items() if value is Required()]
    if required_args:
        raise MissingRequiredArgsError(required_args)
    return True

def main(args=None):
    args = args if args is None else sys.argv[1:]
    parser = ArgumentParser(
        description=__doc__,
        formatter_class=RawDescriptionHelpFormatter,
        add_help=False)
    parser.add_argument('--debug',
        action='store_true',
        help='default="%(default)s"; toggle debug mode on')
    parser.add_argument('--verbose',
        action='store_true',
        help='default="%(default)s"; toggle verbose mode on')
    parser.add_argument('--config',
        metavar='FILEPATH',
        default='~/.config/%(NAME)s/%(NAME)s.yml' % globals(),
        help='default="%(default)s"; config filepath')
    template_group = parser.add_argument_group(title='template options')
    template_group = template_group.add_mutually_exclusive_group(required=False)
    add_argument(template_group, '-F', '--template-file')
    add_argument(template_group, '-N', '--template-name')

    ns, rem = parser.parse_known_args(args)

    config = defaults_load(ns.config)
    template = defaults_load(ns.template_file)

    parser = ArgumentParser(
        parents=[parser])

    parser.set_defaults(**config)

    subparsers = parser.add_subparsers(
        dest='command',
        title='commands',
        description='choose a command to run')

    add_create(subparsers, template)
    add_show(subparsers, template)

    if ns.verbose:
        pprint(dict(config=config))
        pprint(dict(template=template))

    ns = parser.parse_args(rem)
    if ns.verbose:
        pprint(dict(ns=ns.__dict__))
    validate(**ns.__dict__)
    if ns.debug:
        print(dumps(ns.__dict__, indent=2, sort_keys=True))
        return 1
    else:
        cr = ChangeRequest()
        return cr.execute(**ns.__dict__)

if __name__ == '__main__':
    main()
