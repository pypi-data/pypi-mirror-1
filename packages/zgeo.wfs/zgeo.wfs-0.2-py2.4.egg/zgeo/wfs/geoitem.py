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

from Acquisition import aq_chain
from zope.event import notify

from shapely.geometry.polygon import Polygon
from shapely.geometry import asShape
from shapely import wkt

from zgeo.geographer.geo import GeoreferencingAnnotator
from interfaces import IWebFeatureServiceable,IWebFeatureService, IWFSGeoItem
from events import WFSGeoreferencedEvent, afterObjectCreated

import logging
logger = logging.getLogger('WFS')

class WFSGeoItem(GeoreferencingAnnotator):
    """ A georeferenced object exposable through WFS
    """
    implements(IWFSGeoItem)
	
    def __init__(self, context):
        """Initialize adapter."""
        self.context = context
        GeoreferencingAnnotator.__init__(self, context)
        self._geom = None
    
	@property
	def id(self):
		return self.context.id
        
    @property
    def name(self):
        return self.context.title_or_id()
    
    @property
    def featureType(self):
        if hasattr(self.context, 'featureType'):
            return self.context.featureType
        if hasattr(self.context, 'getFeatureType'):
            return self.context.getFeatureType()
        return 'default'
        
    @property
    def uri(self):
        return self.context.absolute_url()
       
    @property
    def geometry(self):
        return self.getGeometry()
    
    @property
    def geometryAsWKT(self):
        """ return geometry as WKT string
        """
        if self.isGeoreferenced():
            return self.getGeometry().wkt
        else:
            return None
        
    @property
    def description(self):
        return getattr(self.context,'description', 'No description')
    
    def getSRS(self):
        # is it correct ??
        srs=self.crs
        if srs is None:
            srs='EPSG:4326'
        return srs

#    def setSRS(self, srs):
#        try:
#            assert (srs.startswith('EPSG') or srs.find('proj') >= 0)
#        except AssertionError:
#            raise ValueError, \
#            "%s is invalid. Spatial reference system definition must be in EPSG or PROJ.4 form" % (srs)
#        self.georef['srs'] = srs
       
    def getGeometry(self):
        if self._geom is None:
            self._geom = asShape(self.geo)
        return self._geom
    
    def setGeoInterface(self, type, coordinates, crs=None):
        GeoreferencingAnnotator.setGeoInterface(self, type, coordinates, crs)
        notify(WFSGeoreferencedEvent(self))
        #notify(afterObjectCreated(self))
        
    def setGeometryFromWKT(self, fromwkt):
        geometry = wkt.loads(fromwkt)
        type = geometry.type
        if type=='Point':
            coords=geometry.coords[0]
        elif type=='Polygon':
            coords=[list(geometry.exterior.coords)]
            logger.info(coords)
        else:
            coords=list(geometry.coords)
        self.setGeoInterface(type, coords)
#    def setGeometry(self, geomtype=None, coords=None, geometry=None, fromwkt=None):
#        if geomtype is None and coords is None and geometry is None and fromwkt is None:
#            raise ValueError, "No parameter provided"
#        if geomtype is not None and coords is not None:
#            try:
#                self._geom = asShape({'type': geomtype,
#                                     'coordinates': coords})
#            except:
#                raise ValueError, "geomtype and coords are inconsistent"
#        elif geometry is not None:
#            try:
#                assert isinstance(geometry, BaseGeometry)
#                self._geom = geometry
#            except AssertionError:
#                raise ValueError, "geometry is not a Shapely object"
#        elif fromwkt is not None:
#            try:
#                self._geom = wkt.loads(fromwkt)
#            except:
#                raise ValueError, "wkt string is inconsistent"
#        self.georef['geometryType'] = self._geom.geometryType()
#        if self.georef['geometryType']=='Point':
#            self.georef['spatialCoordinates'] = self._geom.coords
#        elif self.georef['geometryType']=='Polygon':
#            self.georef['spatialCoordinates'] = None
#        else:
#            self.georef['spatialCoordinates'] = list(self._geom.coords)
#            
#        notify(GeoreferencedEvent(self))
        
    def isGeoreferenced(self):
        """Return True if the object is "on the map"."""
        return self.coordinates is not None
    
    def getGML(self):
        """ return geometry as GML string
        """
        if self.isGeoreferenced():
            coords=self.coordinates
                
            logger.info(str(coords))
            
            #PART TO FACTORIZE WITH GETGMLBOUNDINGBOX (WFS.py)
            bboxTuple=bboxAsTuple(self.getGeometry())
            strbbox=str(bboxTuple[0])+','+str(bboxTuple[1])+' '+str(bboxTuple[2])+','+str(bboxTuple[3])
            wfs=self.getWFSParent()
            if self.type == 'Polygon':
                outerCoords=coords[0]
                outerPoints=[str(p[0])+","+str(p[1]) for p in outerCoords]
                logger.info((" ").join(outerPoints))
                gml = '<myns:'+self.featureType+' id="'+self.id+'">'
                gml += '<gml:boundedBy> <gml:Box srsName="'+self.getSRS()+'"> <gml:coordinates>'+strbbox+'</gml:coordinates> </gml:Box></gml:boundedBy>'
                gml += '<myns:msGeometry><gml:'+self.type+' srsName="'+wfs.srs+'">'
                gml += '<gml:outerBoundaryIs><gml:LinearRing><gml:coordinates>'+(" ").join(outerPoints)+'</gml:coordinates></gml:LinearRing></gml:outerBoundaryIs>'
                gml += '</gml:'+self.type+'> </myns:msGeometry>'+self.getGMLElement()+'</myns:'+self.featureType+'>' 
            elif self.type == 'Point':
                coords=[coords]
                points=[str(p[0])+","+str(p[1]) for p in coords]
                gml = '<myns:'+self.featureType+' id="'+self.id+'"> <gml:boundedBy> <gml:Box srsName="'+self.getSRS()+'"> <gml:coordinates>'+strbbox+'</gml:coordinates> </gml:Box> </gml:boundedBy> <myns:msGeometry> <gml:'+self.type+' srsName="'+wfs.srs+'"> <gml:coordinates>'+(" ").join(points)+'</gml:coordinates> </gml:'+self.type+'> </myns:msGeometry>'+self.getGMLElement()+'</myns:'+self.featureType+'>' 
            else:
                points=[str(p[0])+","+str(p[1]) for p in coords]
                gml = '<myns:'+self.featureType+' id="'+self.id+'"> <gml:boundedBy> <gml:Box srsName="'+self.getSRS()+'"> <gml:coordinates>'+strbbox+'</gml:coordinates> </gml:Box> </gml:boundedBy> <myns:msGeometry> <gml:'+self.type+' srsName="'+wfs.srs+'"> <gml:coordinates>'+(" ").join(points)+'</gml:coordinates> </gml:'+self.type+'> </myns:msGeometry>'+self.getGMLElement()+'</myns:'+self.featureType+'>' 

            return gml
        else:        
            #No geometry for this object
            return ''
        
    def getGMLElement(self):
        gml=''
        wfs=self.getWFSParent()
        for element in wfs.getElements(self.featureType):
            attr=getattr(self, element)
            if callable(attr):
                attr=attr()
            gml=gml+'<myns:'+element+'>'+str(attr)+'</myns:'+element+'>'
        return gml
    
    def __getattr__(self,name):
        """Overloads getattr to return context attibutes
        """
        if hasattr(self.context, name):
            return getattr(self.context, name)
        elif hasattr(self.context, 'get'+name.capitalize()):
            return getattr(self.context, 'get'+name.capitalize())()
#        else:
#            return self.__dict__[name]

    def getWFSParent(self):
        """
        """
        parents = self.context.aq_chain
        isWFSenabled = False    
        for o in parents:
            if IWebFeatureServiceable.providedBy(o):
                isWFSenabled = True
                break
        if isWFSenabled:
            return IWebFeatureService(o)
        else:
            return None

def bboxAsTuple(geometry):
    """ return the geometry bbox as tuple
    """
    envelope=geometry.envelope
    if envelope.geometryType()=="Point":
        x=envelope.coords[0][0]
        y=envelope.coords[0][1]
        return (x,y,x,y)
    else:
        return envelope.bounds
	
def bboxFromTuple(bbox_tuple):
	coords = ((bbox_tuple[0], bbox_tuple[1]),
			  (bbox_tuple[0], bbox_tuple[3]),
			  (bbox_tuple[2], bbox_tuple[3]),
			  (bbox_tuple[2], bbox_tuple[1]))
	return Polygon(coords)