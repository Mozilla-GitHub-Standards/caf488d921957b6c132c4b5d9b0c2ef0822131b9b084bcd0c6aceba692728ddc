#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

from cr.utils.shell import call

def get_version():
    try:
        reporoot = call('git rev-parse --show-toplevel')[1].strip()
        try:
            value = open(os.path.join(reporoot, 'VERSION')).read().strip()
            return value
        except:
            value = call('git describe --abbrev=7')[1].strip()
    except:
        value ='UNKNOWN'
    return value

class Version(str):
    __instance = None
    def __new__(cls):
        if Version.__instance is None:
            value = get_version()
            Version.__instance = super(Version, cls).__new__(cls, value)
        return Version.__instance

version = Version()
