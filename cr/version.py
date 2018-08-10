#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from cr.utils.shell import call

class Version(object):
    __instance = None
    def __new__(cls):
        if Version.__instance is None:
            try:
                value = call('git describe')[1].strip()
            except:
                value ='UNKNOWN'
            Version.__instance = object.__new__(cls)
        Version.__instance.value = value
        return Version.__instance
    def __repr__(self):
        return self.value

version = Version()
