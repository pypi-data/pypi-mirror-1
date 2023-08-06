# -*- coding: utf-8 -*-
from geomobilejp.converter.datum import convert, Point

def test_convert1():
    p1 = Point('35.20.51.664', '138.34.56.905', 'tokyo')
    p2 = convert(p1, 'wgs84').to_format('dms')

    assert p2.latitude == '35.21.03.342'
    assert p2.longitude == '138.34.45.725'

def test_convert2():
    p1 = Point('+35.65580', '+139.65580', 'wgs84')
    p2 = convert(p1, 'tokyo').to_format('dms')

    assert p2.latitude == '35.39.09.225'
    assert p2.longitude == '139.39.32.434'

def test_convert3():
    p1 = Point('-35.20.51.664', '138.34.56.905', 'wgs84')
    p2 = p1.to_format('dms')
    assert p2.latitude == '-35.20.51.664'
    assert p2.longitude == '138.34.56.905'

def test_convert4():
    p1 = Point('35.65580', '-139.65580', 'wgs84')
    p2 = convert(p1, 'wgs84').to_format('dms')
    assert p2.latitude == '35.39.20.880'
    assert p2.longitude == '-139.39.20.880'

def test_convert5():
    p1 = Point('35.20.51.664', '138.34.56.905', 'wgs84')
    p2 = p1.to_format('degree')
    assert p2.latitude == 35.347684
    assert p2.longitude == 138.582474

def test_convert6():
    p1 = Point('-35.20.51.664', '138.34.56.905', 'wgs84')
    p2 = p1.to_format('degree')
    assert p2.latitude == -35.347684
    assert p2.longitude == 138.582474

def test_convert7():
    p1 = Point('35.20.51.664', '-138.34.56.905')
    p2 = p1.to_format('degree')
    assert p2.latitude == 35.347684
    assert p2.longitude == -138.582474

def test_convert8():
    p1 = Point('-35.20.51.664', '-138.34.56.905')
    p2 = p1.to_format('degree')
    assert p2.latitude == -35.347684
    assert p2.longitude == -138.582474

def test_convert9():
    p1 = Point('35.20.51.664', '-138.34.56.905')
    p2 = p1.to_format('dms')
    assert p2.latitude == '35.20.51.664'
    assert p2.longitude == '-138.34.56.905'
