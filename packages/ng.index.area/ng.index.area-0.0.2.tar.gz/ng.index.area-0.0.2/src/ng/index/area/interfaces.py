### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Interfaces for the Zope 3 based ng.index.area package

$Id: interfaces.py 52832 2009-04-06 10:00:30Z corbeau $
"""
__author__  = "Yegor Shershnev, 2009"
__license__ = "GPL"
__version__ = "$Revision: 52832 $"

from zope.schema import Float, Tuple
from zope.app.catalog.interfaces import IAttributeIndex
from zope.interface import Interface


# May be useful
class ICoordinates(Interface) :

    x = Float(title = u"Latitude")
    
    y = Float(title = u"Logtitude")


class IAreaIndex(IAttributeIndex) :

    pass


class IGeolocation(Interface) :

    location = Tuple(
        title = u"Location",
        description = u"Location of object",
        value_type = Float())
