### -*- coding: utf-8 -*- #############################################
#######################################################################
"""Product class for the Zope 3 based product package

$Id: areaindex.py 52865 2009-04-07 14:50:22Z cray $
"""
__author__  = "Yegor Shershnev, 2009"
__license__ = "GPL"
__version__ = "$Revision: 52865 $"

from zope.interface import implements
from zope.app.catalog.interfaces import ICatalogIndex
from interfaces import IAreaIndex
from persistent import Persistent
from zope.app.container.contained import Contained
from zope.index.interfaces import IInjection, IStatistics, IIndexSearch
from zope.app.catalog.attribute import AttributeIndex
from areabase import AreaBase
from BTrees.IOBTree import IOBTree
from math import sqrt
from zope.component import getUtility
from zope.app.intid.interfaces import IIntIds
from zope.location.interfaces import ILocation
from geoellipsoidprojection import GeoEllipsoidProjection


class AreaIndexBase(AreaBase, Persistent, Contained) :

    implements(IAreaIndex, ICatalogIndex, IInjection, IStatistics, IIndexSearch)

    interface = None
    
    field_name = ""

    field_callable = False
    
    def __init__(self, *args, **kw) :
        super(AreaIndexBase, self).__init__(self, *args, **kw)
        self.data = IOBTree()
    
    def index_doc(self, docid, value) :
        if docid in self.data.keys() :
            del self.data[docid]
        lst = []
        self.data[docid] = ((value[0],value[1]), lst)
        keys = list(self.data.keys())
        keys.remove(docid)
        
        for key in keys :
            x1, y1 = value
            x2, y2 = self.data[key][0]
            #dist = sqrt(pow((x2-x1),2) + pow((y2-y1),2))
            dist = GeoEllipsoidProjection(x1, y1, x2, y2)
            lst.append((dist, key))
            self.data[key][1].append((dist, docid))
            self.data[key][1].sort()
        
        lst.sort()
    
    def unindex_doc(self, docid) :
        try :
            del self.data[docid]
        except KeyError, msg:
            print "KeyError", msg
            pass
    
    def clear(self) :
        for key in self.data.keys() :
            del self.data[key]
    
    def apply(self, query) :
        ob = query['object']
        dist = query['dist']
        
        ids = getUtility(IIntIds, context=ILocation(self).__parent__)
        try:
            docid = ids.getId(ob)
        except KeyError:
            return []
        
        result = []
        
        for i, j in self.data[docid][1] :
            if i < dist:
                result.append(j)

        return result
    
    def documentCount(self) :
        return len(self.data)
    
    def wordCount(self) :
        return pow(len(self.data), 2)


class AreaIndex(AttributeIndex, AreaIndexBase) :

    pass
