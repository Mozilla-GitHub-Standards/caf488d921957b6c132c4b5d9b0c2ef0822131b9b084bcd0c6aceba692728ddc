#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from cr.utils.shell import call

try:
    version = call('git describe')[1].strip()
except:
    version ='UNKNOWN'
