#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

class ChangeRequest(object):
    def __init__(self):
        pass

    def execute(self, ns):
        return {
            'create': self.create,
            'show': self.show,
        }[ns.command](ns)

    def create(self, ns):
        pass

    def show(self, ns):
        pass
