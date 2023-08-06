### -*- coding: utf-8 -*- #############################################
#######################################################################
"""GeoEllipsoidProjection function for the Zope 3 based ng.index.area package

$Id: geoellipsoidprojection.py 52834 2009-04-06 11:15:34Z corbeau $
"""
__author__  = "Yegor Shershnev, 2009"
__license__ = "GPL"
__version__ = "$Revision: 52834 $"

from math import cos, sqrt, pi

def GeoEllipsoidProjection(x1, y1, x2, y2) :

    fi = ((x1 + x2) / 2) * (pi / 180)

    k1 = 111.13209 - 0.56605 * cos(2 * fi) + 0.00120 * cos(4 * fi)
    k2 = 111.41513 * cos(fi) - 0.09455 * cos(3 * fi) + 0.00012 * cos(5 * fi)

    dx = (x2 - x1)
    
    dy = (y2 - y1)

    dist = sqrt(pow((k1 * dx), 2) + pow((k2 * dy), 2))
    print "\n\n\n\n\n", dist
    return dist
