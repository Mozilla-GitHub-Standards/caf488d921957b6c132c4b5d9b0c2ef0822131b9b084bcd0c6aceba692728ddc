#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import sys
sys.dont_write_bytecode = True

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
from datetime import datetime
from argparse import ArgumentParser, RawDescriptionHelpFormatter

from cr import ChangeRequest, required
from cr.constants import *
from cr.utils.json import print_json
from cr.version import version

class DatetimeError(Exception):
    def __init__(self, string):
        msg = fmt('the string={string} could not be converted to ISO 8601')
        super(DatetimeError, self).__init__(msg)

def date(string):
    try:
        datetime.strptime(string, ISO_8601)
    except ValueError as ve:
        raise DatetimeError(string)
    return string

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

def validate(**kwargs):
    return [arg for arg, value in kwargs.items() if value is required]

def add_create(subparsers, *defaults):
    parser = subparsers.add_parser('create')

    required_group = parser.add_argument_group(title='questionnaire required')
    required_group.add_argument(
        '-S', '--planned-start-date',
        metavar='DATE',
        default=required,
        type=date,
        help='enter planned start date (ISO 8601)')
    required_group.add_argument(
        '-E', '--planned-end-date',
        metavar='DATE',
        default=required,
        type=date,
        help='enter planned end date (ISO 8601)')
    required_group.add_argument(
        '-C', '--change-plan',
        metavar='PLAN',
        default=required,
        help='enter in text regarding the change plan if it is applicable')
    required_group.add_argument(
        '-D', '--short-description',
        metavar='DESC',
        default=required,
        help='enter in text regarding the short description if it is applicable')
    required_group.add_argument(
        '-B', '--business-impact',
        metavar='IMPACT',
        default=required,
        choices=BUSINESS_IMPACT,
        help='default="%(default)s"; choose the business impact from [%(choices)s]')
    required_group.add_argument(
        '-I', '--change-impact',
        metavar='IMPACT',
        default=required,
        choices=CHANGE_IMPACT,
        help='default="%(default)s"; choose the impact from [%(choices)s]')

    optional_group = parser.add_argument_group(title='questionnaire optional')
    optional_group.add_argument(
        '-u', '--user-impact',
        metavar='IMPACT',
        default=USER_IMPACT[0],
        choices=USER_IMPACT,
        help='default="%(default)s"; choose the user-impact from [%(choices)s]')
    optional_group.add_argument(
        '-s', '--security-risk-level',
        metavar='LEVEL',
        default=SECURITY_RISK_LEVEL[0],
        choices=SECURITY_RISK_LEVEL,
        help='default="%(default)s"; choose the security risk level from [%(choices)s]')
    optional_group.add_argument(
        '-f', '--change-frequency',
        metavar='FREQ',
        default=CHANGE_FREQUENCY[0],
        choices=CHANGE_FREQUENCY,
        help='default="%(default)s"; choose the change frequency from [%(choices)s]')
    optional_group.add_argument(
        '-t', '--test-plan',
        metavar='PLAN',
        help='enter in text regarding the test plan if it is applicable')
    optional_group.add_argument(
        '-p', '--post-implementation-plan',
        metavar='PLAN',
        help='enter in text regarding the post implementation plan, if applicable')
    optional_group.add_argument(
        '-e', '--customer-end-user-plan',
        metavar='PLAN',
        help='enter in text regarding the customer / end-user plan, if applicable')
    optional_group.add_argument(
        '-r', '--rollback-procedure',
        metavar='PROC',
        help='enter in text regarding the rollback procedure')
    optional_group.add_argument(
        '-R', '--peer-review-date',
        metavar='DATE',
        type=date,
        help='enter peer-review date (ISO 8601), if applicable')
    optional_group.add_argument(
        '-v', '--vendor-name',
        metavar='NAME',
        help='enter the vendor name, if applicable')
    optional_group.add_argument(
        '-d', '--planned-downtime',
        action='store_true',
        help='default="%(default)s"; toggle if previous change was successfully performed in downtime window')

    for d in defaults:
        parser.set_defaults(**d)
    return parser

def add_show(subparsers, *defaults):
    parser = subparsers.add_parser('show')
    parser.add_argument(
        '--show-arg1',
        help='show arg1')
    parser.add_argument(
        '--show-arg2',
        help='show arg2')

    for d in defaults:
        parser.set_defaults(**d)
    return parser

def add_subparsers(parser):
    subparsers = parser.add_subparsers(
        dest='command',
        title='commands',
        description='choose a command to run')
    subparsers.required = True
    return subparsers

def main(args=None):
    args = args if args is None else sys.argv[1:]
    parser = ArgumentParser(add_help=False)

    parser.add_argument('--version',
        action='version',
        version='change-request ' + version)
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

    template_group = parser\
        .add_argument_group(title='template options')\
        .add_mutually_exclusive_group(required=False)
    template_group.add_argument(
        '-F', '--template-file',
        metavar='FILE',
        help='path to template file')
    template_group.add_argument(
        '-N', '--template-name',
        metavar='NAME',
        help='name of template stored on server')

    ns, rem = parser.parse_known_args(args)

    config = defaults_load(ns.config)
    template = defaults_load(ns.template_file)

    parser = ArgumentParser(
        parents=[parser],
        description=__doc__,
        formatter_class=RawDescriptionHelpFormatter)

    parser.set_defaults(**config)

    subparsers = add_subparsers(parser)
    add_create(subparsers, template, ns.__dict__) #FIXME: it seems like we
    add_show(subparsers, template, ns.__dict__) # shouldn't have to pass ns here

    ns = parser.parse_args(rem)

    required_args = validate(**ns.__dict__)
    if required_args:
        print('required args missing:\n  ' + '\n  '.join(required_args))
        return 1

    if ns.debug:
        print_json(ns.__dict__)
        return 1
    else:
        cr = ChangeRequest()
        return cr.execute(**ns.__dict__)

if __name__ == '__main__':
    sys.exit(main())
