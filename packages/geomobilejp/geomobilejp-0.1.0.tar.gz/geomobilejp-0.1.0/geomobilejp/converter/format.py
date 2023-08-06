# -*- coding: utf-8 -*-
import re
from math import floor

DMS_LATITUDE_RE = re.compile(r'^[\-\+NS]?\d{1,2}\.\d{1,2}.\d{1,2}(?:\.\d+)$', re.I)
DMS_LONGITUDE_RE = re.compile(r'^[\-\+EW]?\d{1,3}\.\d{1,2}.\d{1,2}(?:\.\d+)$', re.I)

DEGREE_LATITUDE_RE = re.compile(r'^[\-\+NS]?\d{1,2}(?:\.\d+)$', re.I)
DEGREE_LONGITUDE_RE = re.compile(r'^[\-\+WE]?\d{1,3}(?:\.\d+)$', re.I)

def _detect_format(lat, lon):
    if DMS_LATITUDE_RE.match(str(lat)) and DMS_LONGITUDE_RE.match(str(lon)):
        return 'dms'
    elif DEGREE_LATITUDE_RE.match(str(lat)) and DEGREE_LONGITUDE_RE.match(str(lon)):
        return 'degree'
    else:
        raise ValueError("Can't detect the format. (%s,%s) is given." % (lat, lon))

def autoformat(latitude, longitude, format):
    if format == 'dms':
        return as_dms(latitude, longitude)
    elif format == 'degree':
        return as_degree(latitude, longitude)
    else:
        raise ValueError('Invalid format name "%s"' % format)

def as_dms(latitude, longitude):
    lat = str(latitude).strip()
    lon = str(longitude).strip()

    format = _detect_format(lat, lon)
    if format == 'dms':
        return (_to_dms(_to_degree(lat)), _to_dms(_to_degree(lon)))
    else:
        return (_to_dms(lat), _to_dms(lon))

def as_degree(latitude, longitude):
    lat = str(latitude).strip()
    lon = str(longitude).strip()

    format = _detect_format(lat, lon)
    if format == 'degree':
        return (float(latitude), float(longitude))
    else:
        return (_to_degree(lat), _to_degree(lon))

def _to_dms(value, digits=3):
    FROM_RE = re.compile(r'^([\-\+NSWE]?)(.+)$', re.I)
    matcher = FROM_RE.match(str(value))
    if not matcher:
        return value

    ws, degree = matcher.groups()

    if ws == '-' or ws in ('W', 'w', 'S', 's'):
        ws = '-'
    else:
        ws = ''

    degree = float(degree)

    deg = floor(degree)
    min = floor((degree - deg) * 60 % 60)

    sec = (degree - deg) * 3600 - min * 60
    zero = (sec < 10) and '0' or ''

    format = '%%s%%d.%%02d.%%s%%%d.%df' % (digits, digits)
    return format % (ws, deg, min, zero, sec)

def _to_degree(value, digits=6):
    TO_RE = re.compile(r'^([\-\+NSWE]?)(\d+)\.(\d+)\.(\d+(?:\.\d+)?)$', re.I)
    matcher = TO_RE.match(str(value))
    if not matcher:
        return value

    ws, deg, min, sec = matcher.groups()
    ret = int(deg) + (int(min) / 60.0) + (float(sec) / 3600.0)

    if ws == '-' or ws in ('W', 'w', 'S', 's'):
        ret *= -1

    format = '%%%d.%df' % (digits, digits)
    return format % ret
