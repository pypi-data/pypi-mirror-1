#!/usr/bin/env python
# ex:ts=4:sw=4:sts=4:et
# -*- tab-width: 4; c-basic-offset: 4; indent-tabs-mode: t -*-
#
# Copyright (C) 2008 Marco Pantaleoni. All rights reserved
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License version 2 as
#    published by the Free Software Foundation.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

"""
python-sflib aviation.py

Simple aviation geodetic computations library.
Computations are based on the great circle model.

North latitudes and West longitudes are considered positive and South and East negative.
The longitude is the opposite of the usual mathematical convention.

Based on http://williams.best.vwh.net/avform.htm

Some coordinates::

  Padova    lat: 45.41667    N (45d 25\' 00\" N)   -> 45.41667
            lon: 11.88333    E (11d 52\' 60\" E)   -> -11.88333
  Vicenza   lat: 45.57527777 N (45d 34\' 31\" N)   -> 45.57527777
            lon: 11.52638888 E (11d 31\' 35\" E)   -> -11.52638888

Example usage:

  >>> pd_lat = 45.41667

  >>> pd_lon = 11.88333

  >>> pd_lat_hms = deg2hms(pd_lat)

  >>> pd_lat_hms
  (45.0, 25.0, 0.012000000012335477)

  >>> pd_lon_hms = deg2hms(pd_lon)

  >>> pd_lon_hms
  (11.0, 52.0, 59.988000000003012)

  >>> hms2deg(pd_lat_hms)
  45.416670000000003

  >>> p_pd = Point(lat=45.41667, lon=-11.88333)

  >>> p_pd
  (45.41667, -11.88333)

  >>> p_vi = Point(lat=45.57527777, lon=-11.52638888)

  >>> p_vi
  (45.57527777, -11.52638888)

  >>> p_pd.distance(p_vi)
  0.0051703243120887867

  >>> p_pd.distance(p_vi) * EARTH_RADIUS
  32940.136192317659

  >>> p_pd.course(p_vi)
  5.2795975204802206

  >>> rad2deg(p_pd.course(p_vi))
  302.49865545125084

  >>> p_vi - p_pd
  (0.0051703243120887867, 5.2795975204802206)

  >>> p_pd - p_vi
  (0.0051703243120887867, 2.1335617563513498)

  >>> p_pd + (0.0051703243120887867, 5.2795975204802206)
  (45.57527777, -11.52638888)

  >>> p_pd + (p_vi - p_pd)
  (45.57527777, -11.52638888)

  >>> p_vi + (p_pd - p_vi)
  (45.41667, -11.88333)

@see: http://williams.best.vwh.net/avform.htm
@see: http://www.koders.com/python/fid0A930D7924AE856342437CA1F5A9A3EC0CAEACE2.aspx?s=coastline
@see: http://en.wikipedia.org/wiki/Spherical_coordinate_system

@author: Marco Pantaleoni
@contact: Marco Pantaleoni <panta@elasticworld.org>
@contact: Marco Pantaleoni <marco.pantaleoni@gmail.com>
@copyright: Copyright (C) 2008 Marco Pantaleoni. All rights reserved.
"""

import math

EARTH_RADIUS_FAI = 6371000.0            # FAI Earth radius (meters)
EARTH_RADIUS_WGS84_EQUATORIAL = 6378137.0 # WGS84 Earth equatorial radius (meters)
EARTH_RADIUS_WGS84_POLAR      = 6356752.0 # WGS84 Earth polar radius (meters)

EARTH_RADIUS = EARTH_RADIUS_FAI

EPS = 1e-8

def deg2rad(angle_deg):
    return (angle_deg / 180.0) * math.pi

def rad2deg(angle_rad):
    return (angle_rad * 180.0) / math.pi

def distance2rad(distance, radius):
    return (distance / radius)

def rad2distance(distance_rad, radius):
    return (distance_rad * radius)

def deg2hms(angle_deg):
    (a_dec, a_int) = math.modf(angle_deg)
    a_dec = math.fabs(a_dec)
    dd = a_int
    (r, mm) = math.modf(a_dec * 60.0)
    ss = r * 60.0
    return (dd, mm, ss)

def hms2deg(hms_tuple):
    (dd, mm, ss) = hms_tuple
    return float(dd) + float(mm) / 60.0 + float(ss) / 3600.0

class EarthModel:
    def __init__(self, radius = EARTH_RADIUS):
        self.radius = radius

class Point(object):
    """
    Geodetic point
    """

    def _get_lat(self):
        return self.__lat
    def _set_lat(self, val):
        self.__lat = val
        self.__lat_r = deg2rad(self.__lat)
    lat = property(_get_lat, _set_lat, None, "latitude in degrees")

    def _get_lon(self):
        return self.__lon
    def _set_lon(self, val):
        self.__lon = val
        self.__lon_r = deg2rad(self.__lon)
    lon = property(_get_lon, _set_lon, None, "longitude in degrees")

    def _get_lat_r(self):
        return self.__lat_r
    def _set_lat_r(self, val):
        self.__lat_r = val
        self.__lat = rad2deg(self.__lat_r)
    lat_r = property(_get_lat_r, _set_lat_r, None, "latitude in radians")

    def _get_lon_r(self):
        return self.__lon_r
    def _set_lon_r(self, val):
        self.__lon_r = val
        self.__lon = rad2deg(self.__lon_r)
    lon_r = property(_get_lon_r, _set_lon_r, None, "longitude in radians")

    def _get_lat_hms(self):
        return deg2hms(self.lat)
    def _set_lat_hms(self, val):
        self.lat = hms2deg(val)
    lat_hms = property(_get_lat_hms, _set_lat_hms, None, "latitude in sexagesimal")

    def _get_lon_hms(self):
        return deg2hms(self.lon)
    def _set_lon_hms(self, val):
        self.lon = hms2deg(val)
    lon_hms = property(_get_lon_hms, _set_lon_hms, None, "longitude in sexagesimal")

    def __init__(self, *args, **kwargs):
        self.lat = 0.0
        self.lon = 0.0
        if ('lat' in kwargs) and ('lon' in kwargs):
            self.lat = kwargs['lat']
            self.lon = kwargs['lon']
        elif ('lat_r' in kwargs) and ('lon_r' in kwargs):
            self.lat_r = kwargs['lat_r']
            self.lon_r = kwargs['lon_r']
        elif ('lat_hms' in kwargs) and ('lon_hms' in kwargs):
            print "A"
            self.lat_hms = kwargs['lat_hms']
            self.lon_hms = kwargs['lon_hms']
        elif len(args) == 2:
            (lat, lon) = args
            self.lat = lat
            self.lon = lon

    def distance(self, p2):
        """
        Return the distance between this point and p2.
        The distance is in radians (range [0:1]).
        """
        return math.acos(math.sin(self.lat_r)*math.sin(p2.lat_r) +
                         math.cos(self.lat_r)*math.cos(p2.lat_r) * math.cos(self.lon_r-p2.lon_r))

    def distance_short(self, p2):
        """
        Return the distance between this point and p2.
        Equivalent to L{distance}, but less subject to rounding errors for short distances.
        The distance is in radians (range [0:1]).
        """
        return 2.0 * math.asin(math.sqrt((math.sin((self.lat_r - p2.lat_r) / 2.0)) ** 2.0 +
                                         (math.cos(self.lat_r) *
                                          math.cos(p2.lat_r) *
                                          (math.sin((self.lon_r - p2.lon_r) / 2.0))) ** 2.0))

    def course(self, p2):
        """
        Return the true course between this point and p2.
        True course is the angle between the course line and the local meridian measured clockwise.
        """
        tc = 0.0
        if math.cos(self.lat_r) < EPS:
            if self.lat_r > 0.0:
                tc = math.pi
            else:
                tc = 2.0 * math.pi
        else:
            d = self.distance(p2)
            if math.sin(p2.lon_r - self.lon_r) < 0.0:
                tc = math.acos((math.sin(p2.lat_r) - math.sin(self.lat_r) * math.cos(d)) /
                               (math.sin(d) * math.cos(self.lat_r)))
            else:
                tc = 2.0 * math.pi - math.acos((math.sin(p2.lat_r) - math.sin(self.lat_r) * math.cos(d)) / (math.sin(d) * math.cos(self.lat_r)))
        return tc

    def add(self, distance, course):
        """
        Return the point with the given distance on the given course from this point.
        """
        lat_r = math.asin(math.sin(self.lat_r)*math.cos(distance)+math.cos(self.lat_r)*math.sin(distance)*math.cos(course))
        dlon = math.atan2(math.sin(course)*math.sin(distance)*math.cos(self.lat_r), math.cos(distance)-math.sin(self.lat_r)*math.sin(lat_r))
        lon_r = math.fmod(self.lon_r - dlon + math.pi, 2.0 * math.pi) - math.pi
        (lat, lon) = (rad2deg(lat_r), rad2deg(lon_r))
        return Point(lat, lon)

    def __add__(self, d_c_tuple):
        (distance, course) = d_c_tuple
        return self.add(distance, course)

    def __sub__(self, p2):
        distance = p2.distance(self)
        course   = p2.course(self)
        return (distance, course)

    def __str__(self):
        return "(%s, %s)" % (self.lat, self.lon)

    __repr__ = __str__

def _test():
    import doctest
    doctest.testmod()

if __name__ == '__main__':
    _test()
