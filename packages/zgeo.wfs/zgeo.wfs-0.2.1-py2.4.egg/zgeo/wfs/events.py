#
# Copyright (c) 2008 Eric BREHAULT
# contact: eric.brehault@makina-corpus.org
#

from zope.interface import implements

from Products.ZCatalog.Catalog import CatalogError

from interfaces import IWebFeatureService, IWebFeatureServiceable, IWFSGeoreferencedEvent
from interfaces import IWFSGeoItem

import logging
logger = logging.getLogger('WFS')

class WFSGeoreferencedEvent(object):
    """Event to notify that object has been georeferenced.
    """
    implements(IWFSGeoreferencedEvent)
    
    def __init__(self, context):
        self.context = context
        
def afterObjectCreated(obj, event):
    """
    """
    geoitem = IWFSGeoItem(obj)
    wfs = geoitem.getWFSParent()
    if wfs is not None:
        cat = wfs.getGeoCatalog()
        #cat.catalog_object(geoitem, obj.absolute_url_path())
        cat.catalog_object(geoitem.context, '/'.join(obj.getPhysicalPath()))
        if geoitem.isGeoreferenced():
            wfs.refreshFeatureTypeBoundingBox(geoitem.featureType, geoitem.getGeometry())
        
def afterObjectModified(obj, event):
    """
    """
    geoitem = IWFSGeoItem(obj)
    wfs = geoitem.getWFSParent()
    if wfs is not None:
        cat = wfs.getGeoCatalog()
        #cat.catalog_object(geoitem,obj.absolute_url_path())
        cat.catalog_object(geoitem.context,'/'.join(obj.getPhysicalPath()))
        wfs.computeFeatureTypeBoundingBox(geoitem.featureType)
        
def afterGeometryModified(event):
    """
    """
    geoitem=event.context
    wfs = geoitem.getWFSParent()
    if wfs is not None:
        cat = wfs.getGeoCatalog()
        #cat.catalog_object(geoitem,obj.absolute_url_path())
        #cat.catalog_object(geoitem,'/'.join(geoitem.context.getPhysicalPath()))
        cat.catalog_object(geoitem.context,'/'.join(geoitem.context.getPhysicalPath()))
        wfs.computeFeatureTypeBoundingBox(geoitem.featureType)
        
def beforeObjectRemoved(obj, event):
    """
    """
    geoitem = IWFSGeoItem(obj)
    wfs = geoitem.getWFSParent()
    if wfs is not None:
        try:
            cat = wfs.getGeoCatalog()
            #cat.uncatalog_object(obj.asolute_url_path())
            uid = '/'.join(obj.getPhysicalPath())
            if cat.getrid(uid):
                cat.uncatalog_object(uid)
            wfs.computeFeatureTypeBoundingBox(geoitem.featureType)
        except:
            logger.info("cannot remove")
            