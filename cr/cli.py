#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
change-request cli

'''

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
from argparse import ArgumentParser, RawDescriptionHelpFormatter, Action

from cr import ChangeRequest, required
from cr.constants import *
from cr.utils.fmt import *
from cr.utils import friendly
from cr.utils.json import json_print
from cr.utils.version import version
from cr.utils.function import docstr
from cr.utils.config import load_config
from cr.utils.git import reporoot
from cr.utils.output import OUTPUT, default_output, output_print

PROJ = 'change-request'
CWD = os.getcwd().replace(os.path.expanduser('~'), '~')
REPOROOT = reporoot()

class ChangeRequestError(Exception):
    pass

class RequiredArgsMissingError(ChangeRequestError):
    def __init__(self, required_args):
        msg = 'required args missing:\n  ' + '\n  '.join(required_args)
        super(RequiredArgsMissingError, self).__init__(msg)

class DateParseError(ChangeRequestError):
    def __init__(self, string):
        msg = fmt('the string={string} could not be converted to ISO_8601')
        super(DateParseError, self).__init__(msg)

class FuturePeerReviewError(ChangeRequestError):
    def __init__(self, string, utcnow):
        msg = fmt('future peer_review_date={string} before utcnow={utcnow} not allowed')
        super(FuturePeerReviewError, self).__init__(msg)

class PlannedStartInPastError(ChangeRequestError):
    def __init__(self, start):
        msg = fmt('error: planned-start {start} is in the past')
        super(PlannedStartInPastError, self).__init__(msg)

class PlannedStopBeforeStartError(ChangeRequestError):
    def __init__(self, stop, start):
        msg = fmt('error: planned-stop {stop} is before planned-start {start}')
        super(PlannedStopBeforeStartError, self).__init__(msg)

class MissingRequiredArgsError(ChangeRequestError):
    def __init__(self, required_args):
        msg = 'missing required args error:\n' + '\n'.join(sorted(required_args))
        super(MissingRequiredArgsError, self).__init__(msg)

class PeerReviewDate(Action):
    def __call__(self, parser, ns, value, option_string=None):
        utcnow = datetime.utcnow()
        review = ISO_8601_to_datetime(value)
        if review > utcnow:
            raise FuturePeerReviewError(value, datetime_to_ISO_8601(utcnow))
        setattr(ns, self.dest, datetime_to_ISO_8601(review))

class PlannedStart(Action):
    def __call__(self, parser, ns, value, option_string=None):
        utcnow = datetime.utcnow()
        if value == 'utcnow':
            stop = utcnow
        elif value.startswith('+'):
            td = friendly.timedelta(value[1:])
            stop = utcnow + td
        else:
            stop = ISO_8601_to_datetime(value)
            if stop < utcnow:
                raise PlannedStartInPastError(value)
        setattr(ns, self.dest, datetime_to_ISO_8601(stop))

class PlannedStop(Action):
    def __call__(self, parser, ns, value, option_string=None):
        if value.startswith('+'):
            start = ISO_8601_to_datetime(ns.planned_start_date)
            td = friendly.timedelta(value[1:])
            stop = start + td
        else:
            stop = ISO_8601_to_datetime(value)
        setattr(ns, self.dest, datetime_to_ISO_8601(stop))

class Required(object):
    __instance = None
    def __new__(cls):
        if Required.__instance is None:
            Required.__instance = object.__new__(cls)
        return Required.__instance
    def __repr__(self):
        return 'Required'

def ISO_8601_to_datetime(string):
    try:
        return datetime.strptime(string, ISO_8601)
    except:
        raise DateParseError(string)

def datetime_to_ISO_8601(dt):
    try:
        return dt.strftime(ISO_8601)
    except:
        raise DateParseError(str(dt))

def validate(**kwargs):
    required_args = [arg for arg, value in kwargs.items() if value is required]
    if required_args:
        raise RequiredArgsMissingError(required_args)

def do_request(ns):
    validate(**ns.__dict__)
    cr = ChangeRequest(**ns.__dict__)
    call = cr.execute()
    output_print(dict(call.recv.json), ns.output)
    return call.recv.status

FRIENDLY_TIMEDELTA = '''
<friendly-timedelta>
allows weeks, days, hours, minutes and seconds to be
represented with an integer [0-9]+ and one of these letters: w, d, h, m, s.
ex. 1w2h30m represents a timedelta of 1 week, 2 hours and 30 minutes
'''
DATETIME_OR_TIMEDELTA = '''
prefix + to friendly-timedelta for date equivalent to {anchor} +timedelta
OR enter future datetime (ISO_8601 format); ex {example}
'''
def add_create(subparsers, *defaults):
    parser = subparsers.add_parser(
        'create',
        description=FRIENDLY_TIMEDELTA)
    parser.add_argument(
        'planned_start_date',
        metavar='planned-start',
        nargs='?',
        default='utcnow',
        action=PlannedStart,
        help='default="%(default)s"; ' + fmt(DATETIME_OR_TIMEDELTA, anchor='utcnow', example='+4h15m OR 2020-1-16T12:30:00Z'))
    parser.add_argument(
        'planned_stop_date',
        metavar='planned-stop',
        action=PlannedStop,
        help=fmt(DATETIME_OR_TIMEDELTA, anchor='planned-start', example='+2w3d8h OR 2056-10-30T7:58:13Z'))

    required_group = parser.add_argument_group(title='questionnaire required')
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
        help='choose the business impact from [%(choices)s]')
    required_group.add_argument(
        '-I', '--change-impact',
        metavar='IMPACT',
        default=required,
        choices=CHANGE_IMPACT,
        help='choose the impact from [%(choices)s]')
    required_group.add_argument(
        '-u', '--user-impact',
        metavar='IMPACT',
        default=required,
        choices=USER_IMPACT,
        help='choose the user-impact from [%(choices)s]')
    required_group.add_argument(
        '-s', '--security-risk',
        metavar='LEVEL',
        default=required,
        choices=SECURITY_RISK,
        help='choose the security risk level from [%(choices)s]')
    required_group.add_argument(
        '-f', '--change-frequency',
        metavar='FREQ',
        default=required,
        choices=CHANGE_FREQUENCY,
        help='choose the change frequency from [%(choices)s]')

    optional_group = parser.add_argument_group(title='questionnaire optional')
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
        action=PeerReviewDate,
        help='enter peer-review date (ISO_8601), if applicable')
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

def add_cr():
    parser = ArgumentParser(add_help=False)

    parser.add_argument(
        '--version',
        action='version',
        version='change-request ' + version)
    parser.add_argument(
        '--debug',
        action='store_true',
        help='default="%(default)s"; toggle debug mode on')
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='default="%(default)s"; toggle verbose mode on')
    parser.add_argument(
        '--config',
        metavar='FILEPATH',
        default=[
            fmt('~/.config/{PROJ}/{PROJ}.yml'),
            fmt('{CWD}/{PROJ}.yml'),
        ],
        help='default="%(default)s"; config filepath')
    parser.add_argument(
        '-O', '--output',
        metavar='OUPUT',
        default=default_output(),
        choices=OUTPUT,
        help='default="%(default)s"; set the output type; choices=[%(choices)s]')
    parser.add_argument(
        '--api-url',
        metavar='URL',
        help='default="%(default)s"; the REST api endpoint url')

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

    return parser

def main(args=None):
    try:
        parser = add_cr()
        ns, rem = parser.parse_known_args(args)

        parser = ArgumentParser(
            parents=[parser],
            description=__doc__,
            formatter_class=RawDescriptionHelpFormatter)
        config = load_config(*ns.config)
        template = load_config(ns.template_file)

        parser.set_defaults(**config)

        subparsers = add_subparsers(parser)
        add_create(subparsers, template, ns.__dict__) #FIXME: it seems like we
        add_show(subparsers, template, ns.__dict__) # shouldn't have to pass ns here

        ns = parser.parse_args(rem)
        status = do_request(ns)
        if status not in HTTP_SUCCESS:
           return status
        return 0

    except ChangeRequestError as cre:
        output_print(dict(errors=[str(cre)]), ns.output)
        return 1

if __name__ == '__main__':
    sys.exit(main())
