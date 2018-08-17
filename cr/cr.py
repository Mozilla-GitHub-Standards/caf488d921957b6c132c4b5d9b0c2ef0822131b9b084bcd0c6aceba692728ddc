#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from attrdict import AttrDict
from urllib.parse import urljoin
from itertools import product

from cr.utils.asyncrequests import AsyncRequests
from cr.utils.json import json_print
from cr.utils.fmt import *

class JsonsDontMatchPathsError(Exception):
    def __init__(self, jsons, paths):
        len_jsons = len(jsons) if isinstance(jsons, list) else None
        len_paths = len(paths) if isinstance(paths, list) else None
        msg = fmt('len(jsons) -> {len_jsons} != len(paths) -> {len_paths}; jsons={jsons}, paths={paths}')
        super(JsonsDontMatchPathsError, self).__init__(msg)

class ChangeRequestPathError(Exception):
    def __init__(self, path_or_paths):
        msg = fmt('error with ChangeRequest param path(s) = {path_or_paths}')
        super(ChangeRequestPathError, self).__init__(msg)

class ChangeRequest(object):
    def __init__(self,
        baseurl=None,
        auth=None,
        headers=None,
        debug=False,
        verbose=False,
        **kwargs):

        self.baseurl = baseurl
        self.auth = auth
        self.headers = headers
        self.debug = debug
        self.verbose = verbose
        self.args = AttrDict(kwargs)
        self.ar = AsyncRequests()

    def keywords(self, path=None, **kw):
        if not path:
            raise ChangeRequestPathError(path)
        kw['url'] = urljoin(self.baseurl, path)
        kw['auth'] = kw.get('auth', self.auth)
        kw['headers'] = kw.get('headers', {
            'Content-Type': 'application/json',
            'User-Agent': 'autocert',
        })
        return kw

    def request(self, method, **kw):
        return self.ar.request(method, **self.keywords(**kw))

    def get(self, path=None, **kw):
        return self.request('GET', path=path, **kw)

    def put(self, path=None, **kw):
        return self.request('PUT', path=path, **kw)

    def post(self, path=None, **kw):
        return self.request('POST', path=path, **kw)

    def delete(self, path=None, **kw):
        return self.request('DELETE', path=path, **kw)

    def requests(self, method, paths=None, jsons=None, **kw):
        if not paths or not hasattr(paths, '__iter__'):
            raise ChangeRequestPathError(paths)
        if jsons:
            if len(jsons) != len(paths):
                raise JsonsDontMatchPathsError(jsons, paths)
            kws = [self.keywords(path=path, json=json, **kw) for (path, json) in product(paths, jsons)]
        else:
            kws = [self.keywords(path=path, **kw) for path in paths]
        return self.ar.requests(method, *kws)

    def gets(self, paths=None, jsons=None, **kw):
        return self.requests('GET', paths=paths, jsons=jsons, **kw)

    def puts(self, paths=None, jsons=None, **kw):
        return self.requests('PUT', paths=paths, jsons=jsons, **kw)

    def posts(self, paths=None, jsons=None, **kw):
        return self.requests('POST', paths=paths, jsons=jsons, **kw)

    def deletes(self, paths=None, jsons=None, **kw):
        return self.requests('DELETE', paths=paths, jsons=jsons, **kw)

    def execute(self):
        return {
            'create': self.create,
            'show': self.show,
        }[self.args.command]()

    def create(self):
        results = [dict(self.args)]
        send = AttrDict(url='url', json=dict(self.args))
        recv = AttrDict(status=200, json=dict(results=results))
        call = AttrDict(response=None, send=send, recv=recv)
        return call

    def show(self):
        raise NotImplementedError
