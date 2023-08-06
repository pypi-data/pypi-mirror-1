#
# Copyright (c) 2007 Eric BREHAULT
# contact: ebrehault@gmail.com
#
# GNU General Public License (GPL)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
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
            