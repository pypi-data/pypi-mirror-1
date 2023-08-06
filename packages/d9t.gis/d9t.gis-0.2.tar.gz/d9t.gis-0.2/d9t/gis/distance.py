# -*- coding: utf-8 -*-
"""
    Author:     D9T
                Daniel Kraft <dk@d9t.de>
                http://d9t.de/
    Date:       2008/04/08
    License:    GPLv3
                This program is free software: you can redistribute it and/or modify
                it under the terms of the GNU General Public License as published by
                the Free Software Foundation, either version 3 of the License, or
                (at your option) any later version.

                This program is distributed in the hope that it will be useful,
                but WITHOUT ANY WARRANTY; without even the implied warranty of
                MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
                GNU General Public License for more details.

                You should have received a copy of the GNU General Public License
                along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
from zope.interface import implements
from interfaces import ICoordinate, IDistanceCalculation
import math

class Distance(object):
    implements(IDistanceCalculation)

    def __init__(self, earth_radius):
        self.earth_radius = earth_radius

    def distance(self, c1, c2):
        c1 = ICoordinate(c1)
        c2 = ICoordinate(c2)
        dst = math.acos(
                        (math.sin(math.radians(c1.latitude)) * math.sin(math.radians(c2.latitude))) +
                        (math.cos(math.radians(c1.latitude)) * math.cos(math.radians(c2.latitude)) * math.cos(math.radians(c1.longitude) - math.radians(c2.longitude)))
                ) * self.earth_radius

        return dst

    def nearest(self, coordinate, coordinate_list, limit=None):
        distances = []
        for c in coordinate_list:
            distances.append( (self.distance(coordinate, c), c))
        distances.sort()
        if limit:
            return distances[:limit]
        return distances


km_distance = Distance(earth_radius=6371.0)
miles_distance = Distance(earth_radius=3959.0)

