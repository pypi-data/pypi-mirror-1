# -*- coding: utf-8 -*-
from math import sin, cos, sqrt, atan2
from point import Point, datum_from_string

RADIAN = 4 * atan2(1, 1) / 180

def convert(point, datum):
    if isinstance(datum, basestring):
        datum = datum_from_string(datum)

    pt = point.to_format('degree')
    d1 = to_datum(pt.datum, pt)
    d2 = datum_from(datum, d1)
    return d2

class Datum(object):
    """
    base class for Datum representation.
    """
    name = ''
    radius = 0
    rate = 0
    translation = (0, 0, 0)

class JGD2000(Datum):
    name = 'jgd2000'

class Tokyo(Datum):
    name = 'tokyo'
    radius = 6377397.155

    r = 1 / 299.152813
    rate = 2 * r - r * r

    translation = (148, -507, -681)

class GRS67(Datum):
    name = 'grs67'
    radius = 6378160
    translation = 0.006694605

class GRS80(Datum):
    name = 'grs80'

    radius = 6378137.0

    r = 1 / 298.257222101
    rate = 2 * r - r * r

class WGS72(Datum):
    name = 'wgs72'

    radius = 6378135

    translation = 0.006694318

class WGS84(Datum):
    name = 'wgs84'

    radius = 6378137

    r = 1 / 298.257223563
    rate = 2 * r - r * r


def to_datum(datum, point):
    height = float(point.height) or 0.0

    lat_sin = sin(float(point.latitude) * RADIAN)
    lat_cos = cos(float(point.latitude) * RADIAN)
    radius_rate = datum.radius / sqrt(1 - datum.rate * lat_sin * lat_sin)

    xy_base = (radius_rate + height) * lat_cos
    x = xy_base * cos(point.longitude * RADIAN)
    y = xy_base * sin(point.longitude * RADIAN)
    z = (radius_rate * (1 - datum.rate) + height) * lat_sin

    trans_x, trans_y, trans_z = datum.translation

    lat = x + (-1 * trans_x)
    lon = y + (-1 * trans_y)
    h = z + (-1 * trans_z)

    new_point = Point(lat, lon, Datum, h)
    return new_point

def datum_from(datum, point):
    trans_x, trans_y, trans_z = datum.translation

    x = float(point.latitude) + trans_x
    y = float(point.longitude) + trans_y
    z = float(point.height) + trans_z

    rate_sqrt = sqrt(1 - datum.rate)

    xy_sqrt  = sqrt(x * x + y * y)
    atan_base = atan2(z, xy_sqrt * rate_sqrt)
    atan_sin = sin(atan_base)
    atan_cos = cos(atan_base)
    lat = atan2(z + datum.rate * datum.radius / rate_sqrt * atan_sin * atan_sin * atan_sin,
                xy_sqrt - datum.rate * datum.radius * atan_cos * atan_cos * atan_cos)
    lng = atan2(y, x)

    lat_sin = sin(lat);
    radius_rate = datum.radius / sqrt(1 - datum.rate * (lat_sin * lat_sin))

    return Point(lat / RADIAN,
                 lng / RADIAN,
                 datum,
                 (xy_sqrt / cos(lat) - radius_rate)
                 )
