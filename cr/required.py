#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class Required(object):
    __instance = None
    def __new__(cls):
        if Required.__instance is None:
            Required.__instance = object.__new__(cls)
        return Required.__instance
    def __repr__(self):
        return 'Required'

required = Required()
