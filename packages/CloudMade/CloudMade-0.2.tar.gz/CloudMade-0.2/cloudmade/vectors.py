#!/usr/bin/env python

from cloudmade import errors, utils
from itertools import chain
import httplib
import urllib


POLYGON = 'polygon'
LINE = 'line'
POINT = 'point'


class Vector(object):

    host = 'alpha.vectors.cloudmade.com'

    def __init__(self, apikey, referrer):
        self.apikey = apikey
        self.referrer = referrer

    def bbox(self, query):
        query = dict(query)
        bbox = ','.join(map(str, utils.revert_bbox(query['bbox'])))
        params = [('zoom', query.get('zoom')),
                  ('styleid', query.get('styleid')),
                  ('coords', query.get('coords')),
                  ('precision', query.get('precision')),
                  ('unused', query.get('unused'))]
        params = [param for param in params if param[1] is not None]
        viewport = query.get('viewport')
        if viewport is not None:
            params.append(('viewport', 'x'.join(map(str, viewport))))
        exclude = query.get('exclude', [])
        if exclude:
            for value in exclude:
                # vectormaps expects coordinates in lon,lat order
                # while most other services expect lat,lon
                params.append(('exclude', ','.join(map(str, utils.revert_bbox(value)))))
        params = urllib.urlencode(params)
        types = ','.join(query.get('types', '*'))
        path = '/%s/%s' % (bbox, types)
        connection = httplib.HTTPConnection(self.host)
        connection.request('GET', "%s?%s" % (path, params))
        response = connection.getresponse()
        if response.status == httplib.OK:
            return response.read()
        else:
            raise errors.HTTPError(response.status, response.reason)

    def tile(self, styleid, size, zoom, xtile, ytile):
        path = '/%s/%s/%d/%d/%d/%d.svgz' % (self.apikey, styleid, size, zoom, xtile, ytile)
        connection = httplib.HTTPConnection(self.host)
        connection.request('GET', path)
        print path
        response = connection.getresponse()
        if response.status == httplib.OK:
            return response.read()
        else:
            raise errors.HTTPError(response.status, response.reason)


class Query(object):

    allowed_types = set([POLYGON, LINE, POINT])

    def __init__(self, bbox):
        self._query = {'bbox': map(float, bbox),
                       'types': set()}

    def __iter__(self):
        return iter(self._query.items())

    def types(self, *values):
        for type_ in values:
            if type_ not in self.allowed_types:
                raise ValueError('Type should be one of %s'
                                 % ', '.join(self.allowed_types))
        self._query['types'].update(values)
        return self

    def viewport(self, width, height):
        self._query['viewport'] = map(int, [width, height])
        return self

    def style(self, id):
        self._query['styleid'] = str(id)
        return self

    def zoom(self, value):
        self._query['zoom'] = int(zoom)
        return self

    def coords(self, value):
        value = str(value)
        if value not in ('rel', 'abs'):
            raise ValueError('coords should be one of "val" or "abs"')
        self._query['coords'] = value
        return self

    def precision(self, value):
        value = int(value)
        if not (0 <= value <= 15):
            raise ValueError('precision should be in range 0..15')
        self._query['precision'] = value
        return self

    def unused(self, value):
        value = str(value)
        if value not in ('hide', 'remove'):
            raise ValueError('coords should be one of "hide" or "remove"')
        self._query['unused'] = value
        return self

    def exclude(self, *bboxes):
        bboxes = [map(float, bbox) for bbox in bboxes]
        if any(len(bbox) != 4 for bbox in bboxes):
            raise ValueError('Expected 4 coordinates in bounding box')
        self._query['exclude'].extend(bboxes)
        return self
