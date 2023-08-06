# -*- coding: utf-8 -*-
from areadata import DATA

def string_from_area(line):
    line = line.strip()
    (code,
     subcode,
     name,
     w, s, e, n,
     second, third, forth, fifth, sixth, seventh,
     rest) = line.split(',', 13)

    return Area(int(code), int(subcode), name, (w, s, e, n), line)

class Area(object):
    def __init__(self, code, subcode, name, rect, meshcache):
        self.code = code
        self.subcode = subcode
        self.name = name
        self.rect = rect
        self.meshcache = meshcache

    def __repr__(self):
        return '<Area %03d-%02d %s>' % (int(self.code),
                                        int(self.subcode),
                                        self.name)

    def __str__(self):
        return '%03d%02d' % (int(self.code),
                             int(self.subcode))

AREA_DATA = [string_from_area(line) for line in DATA.split('\n')]
