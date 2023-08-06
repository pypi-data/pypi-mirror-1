#!/usr/bin/env python

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

class APIKeyMissingError(Exception):
    """Raised when API key is not specified in Connection constructor"""
    pass

class ObjectNotFound(Exception):
    """Raised when object was not found by geocoding service"""
    pass

class HTTPError(Exception):
    """Raised when HTTP code other than 200 returned"""
    pass

class RouteNotFound(Exception):
    """Raised when specified route couldn't be found"""
    pass

class GeometryParseError(Exception):
    """Raised when geometry is malformed"""
    pass
