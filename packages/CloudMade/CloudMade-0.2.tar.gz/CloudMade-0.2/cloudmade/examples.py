#!/usr/bin/env python

"""Example usage of CloudMade's python API"""

__license__ = """
Copyright 2009 CloudMade.

Licensed under the GNU Lesser General Public License, Version 3.0;
You may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.gnu.org/licenses/lgpl-3.0.txt

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import tile
import geometry
import routing
import geocoding
import exception
import connection

if __name__ == '__main__':
    print "Starting examples"
    print
    
    conn = connection.Connection(apikey="BC9A493B41014CAABB98F0471D759707")
    
    print "Looking for Potsdamer Platz in Berlin, Germany:"
    geo_results = geocoding.find("Potsdamer Platz,Berlin,Germany", results=5,
                             skip=0, connection=conn)
    geoobject = geo_results.results[0]
    print "Properties of the most relevant found object: %r" % geoobject.properties
    print "It's coordinates: %r" % geoobject.centroid
    print

    library = geocoding.find_closest('library', geometry.Point([51.66117, 0.1]),
                                 return_geometry=True, connection=conn)
    print library.properties
    print library.centroid
    try:
        geocoding.find_closest('library', geometry.Point([59.12, 81.1]),
                               return_geometry=True, connection=conn)
    except exception.ObjectNotFound, exc:
        print "Couldn't find any library close to following coordinates: 59.12, 81.1"
    print

    print "Looking for simple route"
    route = routing.get_route(start=geometry.Point([47.25976, 9.58423]),
                            end=geometry.Point([47.66117, 9.99882]),
                            type_="car", type_modifier="shortest",
                            connection=conn)
    print route.summary.total_distance
    print route.summary.start_point
    print route.summary.end_point
    print

    print "Looking for route with several transition points"
    transit_points = [geometry.Point([51.22, 4.41]), geometry.Point([51.2, 4.41])]
    route = routing.get_route(start=geometry.Point([51.22545, 4.40730]),
                            end=geometry.Point([51.23, 4.42]),
                            transit_points=transit_points,
                            type_="car", type_modifier="shortest",
                            connection=conn)
    print route.summary.total_distance
    print route.summary.start_point
    print route.summary.end_point
    print
    
    print "Simple tile "
    png = tile.get_tile(47.26117, 9.59882, 10, tile_size=256, connection=conn)
    open('example.png', "wb").write(png)
