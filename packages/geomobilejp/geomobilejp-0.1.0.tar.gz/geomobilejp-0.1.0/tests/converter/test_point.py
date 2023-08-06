# -*- coding: utf-8 -*-
from geomobilejp.converter import Point, datum

def test_datum():
    pt = Point(35.65580, 139.65580, 'tokyo')
    assert pt.datum == datum.Tokyo

    pt = Point(35.65580, 139.65580, datum.Tokyo)
    assert pt.datum == datum.Tokyo

    pt = Point(35.65580, 139.65580, 'wgs84')
    assert pt.datum == datum.WGS84

    pt = Point(35.65580, 139.65580, datum.WGS84)
    assert pt.datum == datum.WGS84

def test_degree():
    pt = Point(35.65580, 139.65580, 'wgs84')

    p1 = pt.to_format('degree')
    assert p1.latitude == 35.65580
    assert p1.longitude == 139.65580

    p2 = pt.to_format('dms')
    assert p2.latitude == '35.39.20.880'
    assert p2.longitude == '139.39.20.880'

def test_dms():
    pt = Point('35.39.24.00', '139.40.15.05', 'wgs84')

    p1 = pt.to_format('degree')
    assert p1.latitude == 35 + (39/60.0) + (24.00/3600.0)
    assert p1.longitude == 139 + (40/60.0) + (15.05/3600.0)

    p2 = pt.to_format('dms')
    assert p2.latitude == '35.39.24.00'
    assert p2.longitude == '139.40.15.05'
