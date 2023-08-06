# -*- coding: utf-8 -*-
from geomobilejp.converter.datum import convert, Point

def test_convert_dms():
    def func(format):
        def inner(args, expected):
            lat, lon, datum = expected
            p1 = Point(*args)
            p2 = p1.convert(datum).to_format(format)
            assert p2.latitude == lat, '%s expected, %s result' % (lat, p2.latitude)
            assert p2.longitude == lon, '%s expected, %s result' % (lon, p2.longitude)
        return inner

    for args, expected in DATA_DMS:
        yield (func('dms'), args, expected)

    for args, expected in DATA_DEGREE:
        yield (func('degree'), args, expected)

DATA_DMS = (
(('35.20.51.664', '138.34.56.905', 'tokyo'),
('35.21.03.342', '138.34.45.725', 'wgs84'),),

(('35.20.39.984328',
'138.35.08.086122',
'tokyo'),
('35.20.51.664',
'138.34.56.905',
'wgs84'),),

(('35.20.51.664',
'138.34.56.905',
'wgs84'),
('35.20.39.985',
'138.35.08.086',
'tokyo'),),

(('35.39.36.145',
'139.39.58.871',
'wgs84'),
('35.39.24.490',
'139.40.10.429',
'tokyo'),),
)

DATA_DEGREE = (
(('35.656667',
'139.670848',
'wgs84'),
(35.653429,
139.674059,
'tokyo'),),
)
