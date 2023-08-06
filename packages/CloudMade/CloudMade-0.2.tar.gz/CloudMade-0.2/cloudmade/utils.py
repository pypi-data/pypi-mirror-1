#!/usr/bin/env python

import math
from cStringIO import StringIO
import gzip

def latlon2tilenums(zoom, point):
    """Convert coordinate pair into tile number"""
    latitude, longitude = map(float, point)
    factor = 2**(zoom - 1)
    latitude, longitude = map(math.radians, (latitude, longitude))
    xtile = 1 + longitude / math.pi
    ytile = 1 - math.log(math.tan(latitude) + (1 / math.cos(latitude))) \
            / math.pi
    return tuple(int(coord * factor) for coord in (xtile, ytile))
    

def tilenums2latlon(xtile, ytile, zoom):
    """Convert tile number into coordinate pair"""
    factor = 2.0 ** zoom
    lon = (xtile * 360 / factor) - 180.0
    lat = math.atan(math.sinh(math.pi * (1 - 2 * ytile / factor)))
    return math.degrees(lat), lon


def revert_bbox(bbox):
    return bbox[1], bbox[0], bbox[3], bbox[2]


def gunzip(string):
    fobj = StringIO(string)
    compressor = gzip.GzipFile(mode='rb', fileobj=fobj)
    return compressor.read()


def filter_params(params):
    for param in params:
        if param[1] is not None:
            yield param
