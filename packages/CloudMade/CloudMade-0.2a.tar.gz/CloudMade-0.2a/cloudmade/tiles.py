#!/usr/bin/env python

from __future__ import absolute_import

import httplib
from cloudmade import utils, errors

class Tile(object):

    host = 'tiles.cloudmade.com'

    def __init__(self, apikey, referrer):
        self.apikey = apikey
        self.referrer = referrer

    def fetch(self, styleid, size, zoom, xtile, ytile):
        path = '/%s/%s/%d/%d/%d/%d.png' % (self.apikey, styleid, size, zoom, xtile, ytile)
        connection = httplib.HTTPConnection(self.host)
        connection.request('GET', path)
        response = connection.getresponse()
        if response.status == httplib.OK:
            return response.read()
        else:
            raise errors.HTTPError(response.status, response.reason)

    def fetch_many(self, styleid, size, zoom, tilenums):
        raise NotImplementedError
