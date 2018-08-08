#!tusr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime

from cr.utils.dictionary import merge

class DatetimeError(Exception):
    def __init__(self, string):
        msg = fmt('the string={string} could not be converted to ISO 8601')
        super(DatetimeError, self).__init__(msg)

ISO_8601 = '%Y-%m-%dT%H:%M:%S%fZ'
def date(string):
    try:
        datetime.strptime(string, ISO_8601)
    except ValueError as ve:
        raise DatetimeError(string)
    return string

USER_IMPACT = [
    '0-10',
    '100-500',
    '500+',
]

SECURITY_RISK_LEVEL = [
    'none/low',
    'medium',
    'high',
]

CHANGE_FREQUENCY = [
    '5+',
    '2-5',
    '0-1',
]

BUSINESS_IMPACT = [
    'uninterrupted',
    'unavailable',
    'intermittent',
    'limited',
    'other',
]

CHANGE_IMPACT =[
    'emergency',
    'critical',
    'essential',
    'recoverable',
]

ARGS = {
    ('-D', '--debug'): dict(
        action='store_true',
        help='default="%(default)s"; toggle debug mode on'
    ),
    ('-V', '--verbose'): dict(
        action='store_true',
        help='default="%(default)s"; toggle verbose mode on'
    ),
    ('-S', '--planned-start-date',): dict(
        metavar='DATE',
        required=True,
        type=date,
        help='enter planned start date (ISO 8601)'
    ),
    ('-E', '--planned-end-date',): dict(
        metavar='DATE',
        required=True,
        type=date,
        help='enter planned end date (ISO 8601)'
    ),
    ('-c', '--change-plan'): dict(
        required=True,
        metavar='PLAN',
        help='enter in text regarding the change plan if it is applicable'
    ),
    ('-d', '--short-description'): dict(
        required=True,
        metavar='DESC',
        help='enter in text regarding the short description if it is applicable'
    ),
    ('-B', '--business-impact'): dict(
        required=True,
        metavar='IMPACT',
        default=BUSINESS_IMPACT[0],
        choices=BUSINESS_IMPACT,
        help='default="%(default)s"; choose the business impact from [%(choices)s]'
    ),
    ('-C', '--change-impact'): dict(
        required=True,
        metavar='IMPACT',
        default=CHANGE_IMPACT[0],
        choices=CHANGE_IMPACT,
        help='default="%(default)s"; choose the impact from [%(choices)s]'
    ),
    ('-U', '--user-impact'): dict(
        metavar='IMPACT',
        default=USER_IMPACT[0],
        choices=USER_IMPACT,
        help='default="%(default)s"; choose the user-impact from [%(choices)s]'
    ),
    ('-P', '--planned-downtime'): dict(
        action='store_true',
        help='default="%(default)s"; toggle if previous change was successfully performed in downtime window'
    ),
    ('-s', '--security-risk-level'): dict(
        metavar='LEVEL',
        default=SECURITY_RISK_LEVEL[0],
        choices=SECURITY_RISK_LEVEL,
        help='default="%(default)s"; choose the security risk level from [%(choices)s]'
    ),
    ('-f', '--change-frequency'): dict(
        metavar='FREQ',
        default=CHANGE_FREQUENCY[0],
        choices=CHANGE_FREQUENCY,
        help='default="%(default)s"; choose the change frequency from [%(choices)s]'
    ),
    ('-t', '--test-plan'): dict(
        metavar='PLAN',
        help='enter in text regarding the test plan if it is applicable'
    ),
    ('-p', '--post-implementation-plan'): dict(
        metavar='PLAN',
        help='enter in text regarding the post implementation plan, if applicable'
    ),
    ('-e', '--customer-end-user-plan'): dict(
        metavar='PLAN',
        help='enter in text regarding the customer / end-user plan, if applicable'
    ),
    ('-r', '--rollback-procedure'): dict(
        metavar='PROC',
        help='enter in text regarding the rollback procedure'
    ),
    ('-R', '--peer-review-date'): dict(
        metavar='DATE',
        type=date,
        help='enter peer-review date (ISO 8601), if applicable'
    ),
    ('-v', '--vendor-name'): dict(
        metavar='NAME',
        help='enter the vendor name, if applicable'
    ),
}

# they can be overridden by supplying kwargs to this function
def add_argument(parser, *sig, **overrides):
    parser.add_argument(
        *sig,
        **merge(ARGS[sig], overrides))
