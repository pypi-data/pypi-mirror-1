# -*- coding: utf-8 -*-
import re

MESH_RE = re.compile(r'^(\d{6})(\d?)(\d?)(\d?)(\d?)(\d?)$')

class Mesh(list):
    def __str__(self):
        return ''.join([str(x) for x in self])

def seek_area(lat, lon, usetokyo=None, format=None):
    from area import AREA_DATA
    mesh = calcurate_mesh(lat, lon, usetokyo, format)
    pattern = ',(%s(%s(%s(%s(%s%s?)?)?)?)?),' % tuple(mesh)
    for area in AREA_DATA:
        if re.search(pattern, area.meshcache):
            return area

    return None

def include_area(area, lat, lon, usetokyo=None, format=None):
    mesh = calcurate_mesh(lat, lon, usetokyo, format)
    matcher = MESH_RE.match(mesh)
    if matcher:
        pattern = ',(%s(%s(%s(%s(%s%s?)?)?)?)?),' % matcher.groups()
        if re.search(pattern, area):
            return True

    return False

def calcurate_mesh(lat, lon, usetokyo=None, format=None):
    """
    Calcurate the mesh of iArea from the given latitude and longitude.
    """
    lat = int(lat * 1000)
    lon = int(lon * 1000)

    # 1st mesh code
    ab = int(lat / 2400000)
    cd = int(lon / 3600000) - 100

    # 2nd mesh code
    x1 = (cd + 100) * 3600000
    y1 = ab * 2400000
    e = int((lat - y1) / 300000)
    f = int((lon - x1) / 450000)

    m = Mesh()
    mesh2 = '%s%s%s%s' % (ab, cd, e, f)
    m.append(mesh2)

    # 3rd mesh code
    x2 = x1 + f * 450000
    y2 = y1 + e * 300000
    l3 = int((lon - x2) / 225000)
    m3 = int((lat - y2) / 150000)
    g = l3 + m3 * 2
    mesh3 = '%s%s' % (mesh2, g)
    m.append(g)

    # 4th meth code
    x3 = x2 + l3 * 225000
    y3 = y2 + m3 * 150000
    l4 = int((lon - x3) / 112500)
    m4 = int((lat - y3) / 75000)
    h = l4 + m4 * 2
    mesh4 = '%s%s' % (mesh3, h)
    m.append(h)

    # 5th mesh code
    x4 = x3 + l4 * 112500
    y4 = y3 + m4 * 75000
    l5 = int((lon - x4) / 56250)
    m5 = int((lat - y4) / 37500)
    i = l5 + m5 * 2
    mesh5 = '%s%s' % (mesh4, i)
    m.append(i)

    # 6th mesh code
    x5 = x4 + l5 * 56250
    y5 = y4 + m5 * 37500
    l6 = int((lon - x5) / 28125)
    m6 = int((lat - y5) / 18750)
    j = l6 + m6 * 2
    mesh6 = '%s%s' % (mesh5, j)
    m.append(j)

    # 7th mesh code
    x6 = x5 + l6 * 28125
    y6 = y5 + m6 * 18750
    l7 = int((lon - x6) / 14062.5)
    m7 = int((lat - y6) / 9375)
    k = l7 + m7 * 2
    mesh7 = '%s%s' % (mesh6, k)
    m.append(k)

    #return mesh7
    return m
