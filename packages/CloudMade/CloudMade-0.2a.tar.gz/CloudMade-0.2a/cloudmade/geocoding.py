#!/usr/bin/env python

from __future__ import absolute_import

import httplib
import urlparse
import urllib
try:
    import json
except ImportError:
    import simplejson as json
from cloudmade import errors


class Geocoder(object):

    host = 'geocoding.cloudmade.com'

    def __init__(self, apikey, referrer):
        self.apikey = apikey
        self.referrer = referrer

    def find(self, query):
        query = dict(query)
        type_ = query.pop('type', 'js')
        params = urllib.urlencode(query)
        path = '/%s/geocoding/v2/find.%s' % (self.apikey, type_)
        connection = httplib.HTTPConnection(self.host)
        connection.request('GET', '%s?%s' % (path, params))
        response = connection.getresponse()
        if response.status == httplib.OK:
            return json.loads(response.read())
        else:
            raise errors.HTTPError(response.status, response.reason)

class Query(object):

    def __init__(self, query=None):
        self._query = {'type': 'js'}
        if query is not None:
            self._query['query'] = query

    def __iter__(self):
        return iter(self._query.items())

    def bbox(self, coords, bbox_only=False):
        """Search in a given bounding box

        If bbox_only is set to False, than results from given bounding box
        will be combined with results from whole planet, but will still have
        higher rank. If set to True, provide results only from bounding box
        """
        if 'around' in self._query:
            raise errors.NotAllowed("'bbox' is not allowed in combination with 'around'")
        coords = map(float, coords)
        if len(coords) != 4:
            raise ValueError('bbox should contain four values')
        self._query['bbox'] = ','.join(map(str, coords))
        self._query['bbox_only'] = str(bool(bbox_only)).lower()
        return self

    def around(self, coord, radius=100):
        """Search around given coordinate or address.
        
        Parameter `radius` controls the radius of search
        """
        if 'bbox' in self._query:
            raise errors.NotAllowed("'around' is not allowed in combination with 'bbox'")
        if isinstance(coord, (list, tuple)):
            try:
                assert len(coord) == 2
                coord = ','.join(map(str, map(float, coord)))
            except AssertionError:
                raise ValueError('Expected coordinate pair')
        else:
            coord = coord.encode('utf8')
        try:
            radius = str(int(radius))
        except (TypeError, ValueError):
            radius = str(radius)
            if radius != 'closest':
                raise ValueError("radius expected to be integer or special value 'closest'")
        self._query['around'] = coord
        self._query['distance'] = radius
        return self

    def skip(self, num):
        """Drop first n values from result"""
        self._query['skip'] = str(int(num))
        return self

    def limit(self, num):
        """Control amount of results that should be retrieved"""
        self._query['results'] = str(int(num))
        return self

    def geometry(self, state):
        """Set this to False if you don't want to retrive geometry""" 
        self._query['return_geometry'] = str(bool(state)).lower()
        return self

    def location(self, value):
        """Flag controlling retrieving location information (city, country, ZIP, etc)"""
        self._query['return_location'] = str(bool(value)).lower()
        return self

    def object_type(self, type):
        """Limit geocoding search to this type of objects"""
        self._query['object_type'] = str(type)
        return self

def structured_address(country=None, county=None, postcode=None,
                       city=None, street=None, house=None, poi=None):
    return ';'.join(':'.join(key, value)
                    for key, value in vars().iteritems())
