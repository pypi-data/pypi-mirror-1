#
# Copyright (c) 2008 Eric BREHAULT
# contact: eric.brehault@makina-corpus.org
#
from OFS.SimpleItem import SimpleItem
from zope.interface import implements
from Products.PluginIndexes.common.util import parseIndexRequest
from Products.PluginIndexes.interfaces import IPluggableIndex
from Products.PluginIndexes.interfaces import ISortIndex
from Products.PluginIndexes.interfaces import IUniqueValueIndex

from BTrees.IIBTree import IITreeSet

from shapely import wkt
from index import BaseIndex 
from zgeo.wfs.geoitem import bboxAsTuple

from zgeo.wfs.interfaces import IWFSGeoItem
import logging
logger = logging.getLogger('WFSCatalog')

class GeometryIndex(SimpleItem, BaseIndex):
    """Index for geometry attribute provided by IWFSGeoItem adapter
    """
    implements(IPluggableIndex, IUniqueValueIndex, ISortIndex)

    meta_type="GeometryIndex"

    query_options = ('query','geometry_operator')

    def __init__(self, id):
        self.id = id
        BaseIndex.__init__(self)
        self.clear()
        self.operators = ('equals', 'disjoint', 'intersects', 'touches', 'crosses', 'within', 'contains', 'overlaps')
        self.useOperator = 'within'
        
    def index_object(self, documentId, obj, threshold=None):
        """Index an object.

        'documentId' is the integer ID of the document.
        'obj' is the object to be indexed.
        """
        returnStatus = 0
            
        geoitem=IWFSGeoItem(obj)
        if geoitem.isGeoreferenced():
            geometry = getattr(geoitem, self.id)
            newValue = geometry.wkt
            if newValue is callable:
                newValue = newValue()
            oldValue = self.backward.get(documentId, None )
            
            if newValue is None:
                if oldValue is not None:
                    self.rtree.delete(documentId, wkt.loads(oldValue).bounds)
                    try:
                        del self.backward[documentId]
                    except ConflictError:
                        raise
                    except:
                        pass
            else:
                if oldValue is not None and newValue!=oldValue:
                    self.rtree.delete(documentId, wkt.loads(oldValue).bounds)
                self.rtree.add(documentId, geometry.bounds)
                self.backward[documentId] = newValue
                
            returnStatus = 1

        return returnStatus

    def unindex_object( self, documentId ):
        """
            Remove the object corresponding to 'documentId' from the index.
        """
        datum = self.backward.get( documentId, None )

        if datum is None:
            return

        self.rtree.delete(documentId, wkt.loads(datum).bounds)
        del self.backward[ documentId ]
        
    def _apply_index(self, request, cid='', type=type):
        """
        """
        record = parseIndexRequest(request, self.id, self.query_options)
        if record.keys==None: return None
        r = None

        operator = record.get('geometry_operator',self.useOperator)
        if not operator in self.operators :
            raise RuntimeError,"operator not valid: %s" % operator
        if operator=='disjoint':
            raise RuntimeError,"DISJOINT not supported yet"

        
        # we only process one key
        key = record.keys[0]
        bbox = bboxAsTuple(key)
        intersection=self.rtree.intersection(bbox)
        set = []
        for d in [int(l) for l in intersection]:
            geom_wkt = self.backward.get( d, None )
            if geom_wkt is not None:
                geom = wkt.loads(geom_wkt)
                if geom is not None:
                    opr=getattr(geom, operator)
                    if opr(key)==1:
                        set.append(d)
        
        r = IITreeSet(set)
        return r, (self.id,)
    
    def destroy_spatialindex(self):
        """
        """
        self.clear()
    