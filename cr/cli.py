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

def add_create(subparsers):
    parser = subparsers.add_parser('create')
    add_argument(parser, '-D', '--debug')
    add_argument(parser, '-V', '--verbose')

    required = parser.add_argument_group(title='questionnaire required')
    add_argument(required, '-S', '--planned-start-date')
    add_argument(required, '-E', '--planned-end-date')
    add_argument(required, '-c', '--change-plan')
    add_argument(required, '-d', '--short-description')
    add_argument(required, '-B', '--business-impact')
    add_argument(required, '-C', '--change-impact')

    optional = parser.add_argument_group(title='questionnaire optional')
    add_argument(optional, '-U', '--user-impact')
    add_argument(optional, '-s', '--security-risk-level')
    add_argument(optional, '-f', '--change-frequency')
    add_argument(optional, '-t', '--test-plan')
    add_argument(optional, '-p', '--post-implementation-plan')
    add_argument(optional, '-e', '--customer-end-user-plan')
    add_argument(optional, '-r', '--rollback-procedure')
    add_argument(optional, '-R', '--peer-review-date')
    add_argument(optional, '-v', '--vendor-name')
    add_argument(optional, '-P', '--planned-downtime')

def add_show(subparsers):
    parser = subparsers.add_parser('show')
    parser.add_argument(
        '--show-arg1',
        help='show arg1')
    parser.add_argument(
        '--show-arg2',
        help='show arg2')

def add_template(subparsers):
    parser = subparsers.add_parser('from-template')
    parser.add_argument(
        'template',
        help='path to template file')

def main(args=None):
    args = args if args else sys.argv[1:]
    parser = ArgumentParser(
        description=__doc__,
        formatter_class=RawDescriptionHelpFormatter,
        add_help=False)
    parser.add_argument(
        '--config',
        metavar='FILEPATH',
        default='~/.config/%(NAME)s/%(NAME)s.yml' % globals(),
        help='default="%(default)s"; config filepath')
    parser.add_argument(
        '--template',
        metavar='FILEPATH',
        help='optional filepath to template with one or more values')

    ns, rem = parser.parse_known_args(args)

    try:
        config = yaml.safe_load(open(ns.config))
    except FileNotFoundError as er:
        config = dict()
    config = defaults_load(ns.config)
    template = defaults_load(ns.template)
    parser = ArgumentParser(
        parents=[parser])
    parser.set_defaults(**config)
    parser.set_defaults(**template)

    subparsers = parser.add_subparsers(
        dest='command',
        title='commands',
        description='choose a command to run')

    add_create(subparsers)
    add_show(subparsers)
    add_template(subparsers)

    ns = parser.parse_args(rem)
    json = ns.__dict__
    command = json.pop('command')
    json.pop('config')
    json.pop('template')
    if json.pop('debug'):
        print(dumps(json, indent=2, sort_keys=True))
        return 1
    else:
        cr = ChangeRequest()
        return cr.execute(ns)

if __name__ == '__main__':
    main()
