#
# Copyright (c) 2007 Eric BREHAULT, Veronique PAYOT
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

from zope.lifecycleevent import ObjectModifiedEvent
from zope.event import notify

from xml.dom import minidom
from xml.dom.minidom import getDOMImplementation

from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
#from Products.Archetypes.utils import make_uuid

from zgeo.wfs.geoitem import bboxAsTuple
from zgeo.wfs.interfaces import IWebFeatureService, IWFSGeoItem
from zgeo.wfs.events import WFSGeoreferencedEvent

import logging
logger = logging.getLogger('WFSView')

WFS_NS = 'http://www.opengis.net/wfs'
GML_NS = 'http://www.opengis.net/gml'
OGC_NS = 'http://www.opengis.net/ogc'

class WebFeatureServiceView(BrowserView):
	""" View on an object to get WFS services
	"""
	
	capabilities = ViewPageTemplateFile('wfs_capabilities.xml')
	describefeaturetype = ViewPageTemplateFile('wfs_featuretype.xml')
	getfeature = ViewPageTemplateFile('wfs_feature.xml')
	config_screen = ViewPageTemplateFile('editFeatureTypes.pt')
	error_message = ViewPageTemplateFile('error.xml')
	
	@property
	def name(self):
		adapted = IWebFeatureService(self.context)
		return adapted.name

	@property
	def title(self):
		adapted = IWebFeatureService(self.context)
		return adapted.title
		
	@property
	def abstract(self):
		adapted = IWebFeatureService(self.context)
		return adapted.abstract
		
	@property
	def onlineresource(self):
		adapted = IWebFeatureService(self.context)
		return adapted.onlineresource
	
	@property
	def srs(self):
		adapted = IWebFeatureService(self.context)
		return adapted.srs
	
	########################
	##  WFS requests handling
	########################
	def wfs(self):
		""" wfs service view
		"""
		adapted = IWebFeatureService(self.context)
		
		# get parameters from querystring
		# (handles case insensitive issues)
		self.readParams()

		# WFS request is contained in a querysting parameter named REQUEST
		req = self.getParam('REQUEST', '').lower()
		postBody = self.request.get('BODY')
		logger.info('wfs request : '+req)
		logger.info('wfs body : ')
		logger.info(postBody)

		# Request Type
		if req == 'getcapabilities':
			self.request.response.setHeader('Content-type','text/xml;charset=utf-8')
			return self.capabilities()
		elif req == 'describefeaturetype':
			self.request.response.setHeader('Content-type','text/xml;charset=utf-8')
			return self.describefeaturetype()
		elif req=='getfeature':
			self.request.response.setHeader('Content-type','text/xml;charset=utf-8')
			strftname=self.getParam('typename')
			if strftname is None:
				return self.reportError('typename field is mandatory')
			else:
				List_ftname=strftname.split(',')
				for ft in List_ftname:
					if ft not in self.getFeaturetypesInfo():
						return self.reportError('This typename is not managed by this service')
									
			error=''
			# Request Parameters
			strbbox=self.getParam('BBOX')
			strfilter=self.getParam('FILTER')
			strmaxFeatures=self.getParam('MAXFEATURES')
			strsortBy=self.getParam('SORTBY')
			
			#MAXFEATURES
			if strmaxFeatures is not None:
				maxFeatures=int(strmaxFeatures)
			else:
				maxFeatures=None
				
			#SORTBY
			if strsortBy is not None:
				sortBy=strsortBy.split(',')
			else:
				sortBy=None
			
			if strbbox is None and strfilter is None:
				#provide all items of Feature Types belonging to List_ftname
				(results,error) = adapted.getFeatureTypeItems(List_ftname,None,None,maxFeatures,sortBy)
				if error is '':
					if len(List_ftname)==1:
						boundingbox=adapted.getFeatureTypeBoundingBox(List_ftname[0])
					else:
						boundingbox=adapted.computeBoundingBoxListFT(List_ftname)
				else:
					return self.reportError(error)
			elif strfilter is None:
				#provide items of Feature Types belonging to List_ftname inside the BBOX
				bbox=map(float,strbbox.split(','))
				if len(bbox)!=4:
					return self.reportError('BBOX must contain 4 float numbers')
				(results,error) = adapted.getFeatureTypeItems(List_ftname, bbox,None,maxFeatures,sortBy)
				boundingbox=adapted.computeBoundingBox(results)
			
			elif strbbox is None:
				#provide items of Feature Types belonging to List_ftname respecting the filter
				xmldom=minidom.parseString(strfilter)
				List_Nodes=xmldom.getElementsByTagName('Filter')
				if len(List_Nodes)!=1: 
					return self.reportError('FILTER Expression Not Well-Formed')
				(results,error)=adapted.getFeatureTypeItems(List_ftname,None,List_Nodes,maxFeatures,sortBy)
				if error is '':
					boundingbox=adapted.computeBoundingBox(results)
				else:
					return self.reportError(error)
			elif strbbox is not None and strfilter is not None:
				xmldom=minidom.parseString(strfilter)
				List_Nodes=xmldom.getElementsByTagName('Filter')
				bbox=map(float,strbbox.split(','))
				if len(bbox)!=4:
					return self.reportError('BBOX must contain 4 float numbers')
				elif len(List_Nodes)!=1: 
					return self.reportError('FILTER Expression Not Well-Formed')
				(results,error)=adapted.getFeatureTypeItems(List_ftname,bbox,List_Nodes,maxFeatures,sortBy)
				if error is '':
					boundingbox=adapted.computeBoundingBox(results)
				else:
					return self.reportError(error)
							
			return self.getfeature(items=results,bbox=boundingbox)
		
		elif postBody is not None:
			xml = minidom.parseString(postBody)
			childs = xml._get_childNodes()
			root = childs[0]
			req = root._get_localName().lower()

			if req == 'getcapabilities':
				self.request.response.setHeader('Content-type','text/xml;charset=utf-8')
				return self.capabilities()
			elif req == 'transaction':
				self.request.response.setHeader('Content-type','text/xml;charset=utf-8')
				return self.transaction(root)
			
		# if no REQUEST, assume getcapabilities
		return self.capabilities()
		
	def getParam(self,param,default=None):
		"""
		"""
		return self._caseinsensitive.get(param.lower(), default)

	def readParams(self):
		"""(from Kai Lautaportti Primagis WMS implementation)
		"""
		logger.info('READPARAM')
		self._caseinsensitive = {}

		for key in self.request.form.keys():
			logger.info('Key : '+key)
			self._caseinsensitive[key.lower()] = self.request.form.get(key)
			logger.info('Value : '+self.request.form.get(key))
			logger.info('Caseinsensitive : '+self._caseinsensitive[key.lower()])
	
	def getGMLFeatureTypeBoundingBox(self,ftname):
		""" return Feature Type Bounding Box as GML string
		""" 
		adapted = IWebFeatureService(self.context)
		bbox=adapted.getFeatureTypeBoundingBox(ftname)
		if bbox is None:
			return ''
		else:
			return self.getGMLBoundingBox(bbox)
	
	def getGMLBoundingBox(self,bbox):
		""" return Bounding Box bbox as GML string
		"""
		if bbox is not None:
			bboxTuple=bboxAsTuple(bbox)
			strbbox=str(bboxTuple[0])+','+str(bboxTuple[1])+' '+str(bboxTuple[2])+','+str(bboxTuple[3])
			gml='<gml:Box srsName="'+self.srs+'"> <gml:coordinates>'+strbbox+'</gml:coordinates> </gml:Box>'
			return gml
	
	def reportError(self, message):
		"""
		"""
		return self.error_message(msg=message)

	def getTupleBoundingBoxFeatureType(self,ftname):
		""" return feature type bounding box as a tuple 
		"""
		adapted = IWebFeatureService(self.context)
		bbox=adapted.getFeatureTypeBoundingBox(ftname)
		if bbox is None:
			return [-180,-90,180,90]
		else:
			return bboxAsTuple(bbox)
		
	########################
	##  Configuration management screen
	########################
	
	def __call__(self):
		action = self.request.get('ACTION')	
		if action=='ADD_FT':
			self.manage_addFeatureType()
		if action=='REMOVE_FT':
			self.manage_removeFeatureTypes()
		if action=='ADD_ELEMENT':
			self.manage_addElementToFeatureType()
		if action=='REMOVE_ELEMENT':
			self.manage_removeElementsFromFeatureType()
		return self.config_screen()
			
			
	def getFeaturetypesInfo(self):
		adapted = IWebFeatureService(self.context)
		return adapted.featuretypes
		
	def transaction(self, transactionNode):
		""" implements the 'transaction' operation 
		"""
		lockIdNodes = transactionNode.getElementsByTagNameNS(WFS_NS, 'LockId')
		insertNodes = transactionNode.getElementsByTagNameNS(WFS_NS, 'Insert')
		updateNodes = transactionNode.getElementsByTagNameNS(WFS_NS, 'Update')
		deleteNodes = transactionNode.getElementsByTagNameNS(WFS_NS, 'Delete')
		
		alterations = {}
		alterations['inserted'] = []
		alterations['updated'] = []
		alterations['deleted'] = []
		
		for n in insertNodes:
			# getting idgen attribute (GenerateNew|UseExisting|ReplaceDuplicate)
			idgen = 'GenerateNew'
			if n.hasAttribute('idgen'):
				idgen = n.attributes['idgen']
			
			features = n._get_childNodes()
			alterations['inserted'].append(self.insertFeaturesGML(idgen, features))

		for n in updateNodes:
			if n.hasAttribute('typeName'):
				typename = n.attributes['typeName'].value
			# TODO: test typeName value
				
			propertyNodes = n.getElementsByTagNameNS(WFS_NS, 'Property')
			filterNodes = n.getElementsByTagNameNS(OGC_NS, 'Filter')
			
			alterations['updated'].append(self.updateFeaturesGML(typename, propertyNodes, filterNodes))

		for n in deleteNodes:
			if n.hasAttribute('typeName'):
				typename = n.attributes['typeName'].value
			# TODO: test typeName value
				
			filterNodes = n.getElementsByTagNameNS(OGC_NS, 'Filter')
			
			alterations['deleted'].append(self.deleteFeaturesGML(typename, filterNodes))

		countInserted = 0
		countUpdated = 0
		countDeleted = 0
		for inserted in alterations['inserted']:
			countInserted += len(inserted)
		for updated in alterations['updated']:
			countUpdated += len(updated)
		for deleted in alterations['deleted']:
			countDeleted += len(deleted)
				
		impl = getDOMImplementation()
		doc = impl.createDocument(WFS_NS, "wfs:TransactionResponse", None)
		root = doc.documentElement
		root.setAttribute("xmlns:wfs", WFS_NS)
		root.setAttribute("xmlns:ogc", OGC_NS)
		root.setAttribute("version", "1.1.0")

		summaryNode =  doc.createElementNS(WFS_NS, 'wfs:TransactionSummary')
		totalInsertedNode =  doc.createElementNS(WFS_NS, 'wfs:totalInserted')
		totalInsertedNode.appendChild(doc.createTextNode(str(countInserted)))
		totalUpdatedNode =  doc.createElementNS(WFS_NS, 'wfs:totalUpdated')
		totalUpdatedNode.appendChild(doc.createTextNode(str(countUpdated)))
		totalDeletedNode =  doc.createElementNS(WFS_NS, 'wfs:totalDeleted')
		totalDeletedNode.appendChild(doc.createTextNode(str(countDeleted)))

		summaryNode.appendChild(totalInsertedNode)
		summaryNode.appendChild(totalUpdatedNode)
		summaryNode.appendChild(totalDeletedNode)
		root.appendChild(summaryNode)

		if countInserted > 0:
			insertResultNode =  doc.createElementNS(WFS_NS, 'wfs:InsertResults')
			for inserted in alterations['inserted']:
				for fid in inserted:
					   featureNode =  doc.createElementNS(WFS_NS, 'wfs:Feature')
					   featureIdNode = doc.createElementNS(OGC_NS, 'ogc:FeatureId')
					   featureIdNode.setAttribute ('fid', fid)
					   featureNode.appendChild(featureIdNode)
					   insertResultNode.appendChild(featureNode)
			root.appendChild(insertResultNode)
		
		response = doc.toprettyxml()
		logger.info(response)

		return response
			

	def insertFeaturesGML(self, idgen, featureNodes):
		""" insert features (insert node from transaction operation) 
		"""
		adapted = IWebFeatureService(self.context)
		inserted = []
		for n in featureNodes:
			typeName = n._get_localName()
			if idgen == 'UseExisting':
				fid = n.getAttributeNS(GML_NS, 'id')
				obj = getattr(self.context, fid)
				# exception if exists
				if obj is not None:
				    return self.reportError('Feature '+fid+' already exists')
			elif idgen == 'ReplaceDuplicate':
				fid = n.getAttributeNS(GML_NS, 'id')
				obj = getattr(self.context, fid)
				# no exception if exists
			else:
				#fid = self.context.invokeFactory('WFSDocument', id=make_uuid(), Title='new Feature')
				fid = self.context.addWFSFeature()
				obj = getattr(self.context, fid)

			obj.featureType = typeName
			propertieNodes = n.childNodes
			for propertieNode in propertieNodes:
				if propertieNode._get_localName() == 'msGeometry':
					wkt = self.getWKTFromGML(propertieNode.firstChild)
					logger.info('insert '+wkt)
		
					geoObj = IWFSGeoItem(obj)
					geoObj.setGeometryFromWKT(wkt)
				else:
					propertyName = propertieNode._get_localName()
					if len(propertieNode.childNodes) > 0:
						propertyValue = propertieNode.childNodes[0].nodeValue
						if hasattr(obj, 'set'+propertyName.capitalize()):
							logger.info('set'+propertyName.capitalize() + "(" + propertyValue+")")
							getattr(obj, 'set'+propertyName.capitalize())(propertyValue)

			inserted.append(fid)

			# reindex
			obj.reindexObject()
			geoObj = IWFSGeoItem(obj)
			notify(WFSGeoreferencedEvent(geoObj))

		return inserted
		
	def updateFeaturesGML(self, typename, propertyNodes, filterNodes):
		""" update features (insert node from transaction operation) 
		"""
		adapted = IWebFeatureService(self.context)

		if len(filterNodes)!=1: 
			return self.reportError('FILTER Expression Not Well-Formed')

		updated = []

		List_ftname = [typename]

		(results,error)=adapted.getFeatureTypeItems(List_ftname, None, filterNodes)

		if error is not '':
			return self.reportError(error)

		for propertyNode in propertyNodes:
			# get property name
			propertyNameNode = propertyNode.getElementsByTagNameNS(WFS_NS, 'Name')[0]
			propertyValueNode = propertyNode.getElementsByTagNameNS(WFS_NS, 'Value')[0]
			propertyName = propertyNameNode.childNodes[0].nodeValue
			logger.info('property '+propertyName.capitalize())

			for result in results:
				obj = result.getObject()
				geoObj = IWFSGeoItem(obj)
				fUpdated = False
	
				# update geometry
				if propertyName == 'msGeometry':
					geomNode = propertyValueNode.firstChild
					wkt = self.getWKTFromGML(geomNode)
					if wkt is not None:
						geoObj.setGeometryFromWKT(wkt)
						fUpdated = True
				if propertyName == 'Title':
					propertyValue = propertyValueNode.childNodes[0].nodeValue
					obj.setTitle(propertyValue)
					fUpdated = True
				else:
					propertyValue = propertyValueNode.childNodes[0].nodeValue
					if hasattr(obj, 'set'+propertyName.capitalize()) and propertyValue is not None:
						getattr(obj, 'set'+propertyName.capitalize())(propertyValue)
						fUpdated = True

				if fUpdated and obj.id not in updated:
					logger.info("update "+obj.id)
					updated.append(obj.id)

		# reindex
		for result in results:
			obj = result.getObject()
			geoObj = IWFSGeoItem(obj)
			obj.reindexObject()
			notify(WFSGeoreferencedEvent(geoObj))
			 
		return updated
		
	def deleteFeaturesGML(self, typename, filterNodes):
		""" delete features (insert node from transaction operation) 
		"""
		adapted = IWebFeatureService(self.context)

		if len(filterNodes)!=1: 
			return self.reportError('FILTER Expression Not Well-Formed')

		deleted = []

		List_ftname = [typename]

		(results,error)=adapted.getFeatureTypeItems(List_ftname, None, filterNodes)

		if error is not '':
			return self.reportError(error)

		for result in results:
			obj = result.getObject()
			geoObj = IWFSGeoItem(obj)

			geoObj.setGeoInterface(None, None, None)
			deleted.append(obj.id)

			# reindex
			obj.reindexObject()
			notify(WFSGeoreferencedEvent(geoObj))
			 
		return deleted
		
	def getWKTFromGML(self, geomNode):
		"""
		"""
		gmlType = geomNode._get_localName().lower()

		#multipointNodes = featureNode.getElementsByTagNameNS(GML_NS, 'MultiPoint')
		#pointNodes = featureNode.getElementsByTagNameNS(GML_NS, 'Point')
		coords = None
		
		if gmlType == 'multipoint':
			coordinates = geomNode.getElementsByTagNameNS(GML_NS, 'coordinates')
			coords = ''
			for coordinate in coordinates:
				value = self.getWKTCoordinateFromGML(coordinate)
				if (coords != ''):
				    coords += ', '+value
				else:
				    coords = value
				
			coords = 'MULTIPOINT('+coords+')'
				
		elif gmlType == 'point':
			coordinates = geomNode.getElementsByTagNameNS(GML_NS, 'coordinates')
			coordinate = coordinates[0]
			coords = self.getWKTCoordinateFromGML(coordinate)
			coords = 'POINT('+coords+')'

		elif gmlType == 'linestring':
			coordinates = geomNode.getElementsByTagNameNS(GML_NS, 'coordinates')
			coordinate = coordinates[0]
			coords = self.getWKTCoordinateFromGML(coordinate)
			coords = 'LINESTRING('+coords+')'

		elif gmlType == 'polygon':
			coords = ''
			outer = geomNode.getElementsByTagNameNS(GML_NS, 'outerBoundaryIs')[0]
			coordinates = outer.getElementsByTagNameNS(GML_NS, 'coordinates')
			for coordinate in coordinates:
				value = '('+self.getWKTCoordinateFromGML(coordinate)+')'
				if (coords != ''):
				    coords += ', '+value
				else:
				    coords = value

			inners = geomNode.getElementsByTagNameNS(GML_NS, 'innerBoundaryIs')
			for inner in inners:
				coordinates = inner.getElementsByTagNameNS(GML_NS, 'coordinates')
				for coordinate in coordinates:
					value = '('+self.getWKTCoordinateFromGML(coordinate)+')'
					if (coords != ''):
						coords += ', '+value
					else:
						coords = value

			coords = 'POLYGON('+coords+')'

		return coords
			
	def getWKTCoordinateFromGML(self, coordinateNode):
		decimal = '.'
		cs = ','
		ts = ' '
		if coordinateNode.hasAttribute('decimal'):
			decimal = coordinateNode.attributes['decimal'].value
		if coordinateNode.hasAttribute('cs'):
			cs = coordinateNode.attributes['cs'].value
		if coordinateNode.hasAttribute('ts'):
			ts = coordinateNode.attributes['ts'].value
		value = coordinateNode.childNodes[0].nodeValue
		return value.replace(ts, '*').replace(cs, ' ').replace('*', ',').replace(decimal, '.')
	
	def getFeatureInfo(self):
		"""
		"""
		info = ""
		if hasattr(self.context, "getWFSFeatureInfo"):
			info = self.context.getWFSFeatureInfo(self.request.get('fid'))
		return info
		
	def manage_addFeatureType(self):
		"""
		"""
		ft=self.request.get('NewFT')
		IWebFeatureService(self.context).addFeatureType(ft)
		
	def manage_removeFeatureTypes(self):
		"""
		"""
		ft_list=self.request.get('FTsToRemove')
		if type(ft_list)==str:
			ft_list=[ft_list]
		IWebFeatureService(self.context).removeFeatureTypes(ft_list)
		
	def manage_addElementToFeatureType(self):
		"""
		"""
		ft=self.request.get('FT')
		elem=self.request.get('NewElem')
		type=self.request.get('NewType')
		IWebFeatureService(self.context).addElementToFeatureType(ft, elem, type)
		
	def manage_removeElementsFromFeatureType(self):
		"""
		"""
		ft=self.request.get('FT')
		elem_list=self.request.get('ElemToRemove')
		if type(elem_list)==str:
			elem_list=[elem_list]
		IWebFeatureService(self.context).removeElementsFromFeatureType(ft, elem_list)		