#!/usr/bin/env python

from __future__ import absolute_import
from cloudmade import geocoding, routing, vectors, tiles, staticmaps

class API(object):

    def __init__(self, apikey, referrer):
        self.apikey = apikey
        self.referrer = referrer
        self.router = routing.Router(apikey, referrer)
        self.geocoder = geocoding.Geocoder(apikey, referrer)
        self.vectors = vectors.Vector(apikey, referrer)
        self.tiles = tiles.Tile(apikey, referrer)
        self.staticmaps = staticmaps.StaticMap(apikey, referrer)

    def find(self, query):
        """Perform geocoding search for a given query"""
        return self.geocoder.find(query)

    def route(self, query):
        """Find a route for a given query"""
        return self.router.route(query)
    
    def tile(self, styleid, size, zoom, xtile, ytile):
        """Fetch tile"""
        return self.tiles.fetch(styleid, size, zoom, xtile, ytile)

    def multitile(self, styleid, size, zoom, tilenums):
        """Fetch several tiles at once"""
        return self.tiles.fetch_many(styleid, size, zoom, tilenums)

    def staticmap(self, query):
        """Fetch staticmap"""
        return self.staticmaps.fetch(query)

    def vector_tile(self, styleid, size, zoom, xtile, ytile):
        """Fetch vector tile"""
        return self.vectors.tile(styleid, size, zoom, xtile, ytile)

    def vector_bbox(self, query):
        """Perform a bounding box query on vector server"""
        return self.vectors.bbox(query)
 
