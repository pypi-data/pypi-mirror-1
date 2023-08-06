#!/usr/bin/env python


from __future__ import absolute_import

import httplib
from cloudmade import utils, errors


class StaticMap(object):

    host = 'staticmaps.cloudmade.com'

    def __init__(self, apikey, referrer):
        self.apikey = apikey
        self.referrer = referrer

    def fetch(self, query):
        query = dict(query)
        raise NotImplementedError


class Query(object):

    def __init__(self, size):
        self._query = {'size': 'x'.join(map(str, map(int, size)))}
