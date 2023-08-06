#!/usr/bin/env python

from __future__ import absolute_import

from cloudmade import errors
import httplib
import urllib
from itertools import chain
try:
    import json
except ImportError:
    import simplejson as json


CAR = 'car'
FOOT = 'foot'
BICYCLE = 'bicycle'


class Router(object):

    host = 'routes.cloudmade.com'

    def __init__(self, apikey, referrer):
        self.apikey = apikey
        self.referrer = referrer

    def route(self, query):
        query = dict(query)
        start_point = '%f,%f' % tuple(query['start_point'])
        end_point = '%f,%f' % tuple(query['end_point'])
        transit_points = ','.join(map(str, chain(*query.get('transit_points', []))))
        if transit_points:
            # Oh, humanity! How come the optional "transit points" is not in
            # URL parameters, but rather in the URL itself?
            points = '%s,[%s],%s' % (start_point, transit_points, end_point)
        else:
            points = ','.join([start_point, end_point])
        route_type = str(query.get('route_type', CAR))
        output_format = str(query.get('output_format', 'js'))
        units = str(query.get('units', 'km'))
        lang = str(query.get('lang', 'en'))
        path = {True: '/%s/api/0.3/%s/%s/shortest.%s',
                False: '/%s/api/0.3/%s/%s.%s'}[query.get('shortest', False)]
        path = path % (self.apikey, points, route_type, output_format)
        params = urllib.urlencode({'lang': lang, 'units': units})
        connection = httplib.HTTPConnection(self.host)
        connection.request('GET', '%s?%s' % (path, params))
        response = connection.getresponse()
        if response.status == httplib.OK:
            response = response.read()
            if output_format == 'js':
                return json.loads(response)
            else:
                return response
        else:
            raise errors.HTTPError(response.status, response.reason)


class Query(object):

    def __init__(self, from_=None, to=None):
        self._query = {}
        if from_ is not None:
            self._query['start_point'] = map(float, from_)
        if to is not None:
            self._query['end_point'] = map(float, to)
        self._query['transit_points'] = []

    def __iter__(self):
        return iter(self._query.items())
        
    def from_(self, coord):
        self._query['start_point'] = map(float, coord)
        return self

    def to(self, coord):
        self._query['end_point'] = map(float, coord)
        return self

    def car(self, shortest=True):
        self._query['route_type'] = CAR
        self._query['shortest'] = shortest
        return self

    def foot(self):
        self._query.pop('shortest', None)
        self._query['route_type'] = FOOT
        return self

    def bicycle(self):
        self._query.pop('shortest', None)
        self._query['route_type'] = BICYCLE
        return self

    def lang(self, specifier):
        self._query['lang'] = str(specifier)
        return self

    def js(self):
        self._query['format'] = 'js'
        return self

    def gpx(self):
        self._query['format'] = 'gpx'
        return self

    def through(self, *coords):
        self._query['transit_points'].extend(coords)
        return self

    def km(self):
        self._query['units'] = 'km'
        return self

    def miles(self):
        self._query['units'] = 'miles'
        return self
