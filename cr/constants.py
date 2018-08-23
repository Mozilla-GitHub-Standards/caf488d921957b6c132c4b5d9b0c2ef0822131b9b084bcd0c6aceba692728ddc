#!/usr/bin/env python3
# -*- coding: utf-8 -*-

ISO_8601 = '%Y-%m-%dT%H:%M:%S%fZ'
ISO_8601 = '%Y-%m-%dT%H:%M:%SZ'

USER_IMPACT = [
    '0-10',
    '100-500',
    '500+',
]

SECURITY_RISK = [
    'low',
    'medium',
    'high',
    'maximum',
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

METHODS = {
    'show': 'GET',
    'create': 'POST',
    'update': 'PUT',
    'remove': 'DELETE',
}

HTTP_SUCCESS = [
    200,
    201,
    202,
    203,
    204,
    205,
]
