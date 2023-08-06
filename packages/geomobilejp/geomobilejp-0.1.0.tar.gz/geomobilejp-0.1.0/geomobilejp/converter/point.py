# -*- coding: utf-8 -*-
import format

DEFAULT_DATUM = 'wgs84'

def datum_from_string(name):
    import datum
    try:
        return {'datum': datum.Datum,
                'tokyo': datum.Tokyo,
                'wgs84': datum.WGS84,
                }[name]
    except KeyError:
        raise ValueError('Invalid datum name "%s"' % name)

def formatter_from_string(name):
    import format
    try:
        return {'degree': format.as_degree,
                'dms'   : format.as_dms,
                }[name]
    except KeyError, e:
        raise ValueError('Invalid format name "%s". Use "degree" or "dms".' % name)

class Point(object):
    def __init__(self, latitude=None, longitude=None, datum=None, height=0):
        self.latitude = latitude or 0.0
        self.longitude = longitude or 0.0
        self.height = height

        if datum is None:
            datum = datum_from_string(DEFAULT_DATUM)
        elif isinstance(datum, basestring):
            datum = datum_from_string(datum)
        self.datum = datum

    def convert(self, datum):
        from datum import convert
        return convert(self, datum)

    def to_format(self, format=None):
        if format is None:
            formatter = format.as_degree
        elif isinstance(format, basestring):
            formatter = formatter_from_string(format)

        lat, lon = formatter(self.latitude, self.longitude)
        return Point(lat, lon, self.datum, self.height)

    def __repr__(self):
        return '<Point lat:%s lon:%s datum:%s>' % (self.latitude,
                                                   self.longitude,
                                                   self.datum.name)
