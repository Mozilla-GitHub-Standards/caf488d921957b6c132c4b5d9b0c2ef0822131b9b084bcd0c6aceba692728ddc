#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

def jsonify(string):
    return json.loads(str(string))

def print_json(d, *exclusions):
    [d.pop(exclusion, None) for exclusion in exclusions]
    print(json.dumps(d, indent=2, sort_keys=True))

