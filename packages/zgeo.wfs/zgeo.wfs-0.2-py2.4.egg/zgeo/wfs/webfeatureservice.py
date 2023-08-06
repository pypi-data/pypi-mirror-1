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

from zope.interface import implements

from shapely import wkt

from zgeo.geographer.interfaces import IGeoCollection

from geoitem import bboxAsTuple, bboxFromTuple
from interfaces import IWebFeatureService, IWebFeatureServiceable
from geocatalog.catalog import GeoCatalog

from Products.AdvancedQuery.AdvancedQuery import *
import re

import logging
logger = logging.getLogger('WFS')

class WebFeatureService(object):
	"""An OGC Web Feature Service adapter
	"""
	implements(IWebFeatureService, IGeoCollection)
	def __init__(self, context):
		"""Initialize adapter."""
		self.context = context
        
	@property
	def name(self):
		return self.context.id

	@property
	def title(self):
		return self.context.Title()
		
	@property
	def abstract(self):
		if hasattr(self.context, 'getAbstract'):
			return self.context.getAbstract()
		else:
			return ''
		
	@property
	def onlineresource(self):
		return self.context.absolute_url()+"/wfs?"
		
	@property
	def srs(self):
		if hasattr(self.context, 'getSrs'):
			return self.context.getSrs()
		else:
			return 'EPSG:4326'
		
	@property
	def featuretypes(self):
		return self.getFeatureTypesDict()
	
	def getFeatureTypesDict(self):
		"""
		"""
		if not hasattr(self.context, 'geoFeaturetypes'):
			ft_dict={'default':
						{'elements': 
							{'Title': 'string'},
						'boundingbox':
							None
						}
					}
			self.context.geoFeaturetypes = ft_dict
		return self.context.geoFeaturetypes
		
	def updateFeatureTypesDict(self, ft_dict):
		"""
		"""
		self.context.geoFeaturetypes = ft_dict

	def getGeoCatalog(self):
		if not hasattr(self.context, 'geoCatalog'):
			cat=GeoCatalog('geoCatalog')
			self.context._setObject('geoCatalog',cat)
		return self.context.geoCatalog
	
	def getElements(self,ftname):
		ft_dict=self.getFeatureTypesDict()
		if ftname in ft_dict:
			return ft_dict[ftname]['elements'].keys()
		return None
	
	def getElementType(self,element):
		""" return the element type from a feature type
		"""
		ft_dict=self.getFeatureTypesDict()
		for ft in ft_dict:
			Elements=self.getElements(ft)
			if element in Elements:
				return ft_dict[ft]['elements'][element]
		return None

	def stringConversionType(self,stringElement,type):
		""" transform a stringElement in a type 
		""" 
		if type=='integer':
			return int(stringElement)
		elif type=='float':
			return float(stringElement)
		return stringElement

	def getQuerySorting(self,sortList):
		""" construct the parameter for sorting in AdvancedQuery from a list 
			(for example:Field1 D,Field2,Field3 D will return ((Field1,'desc'),(Field2,'asc'),(Field3','desc')))
		"""
		querySorting=[]
		if sortList is not None:
			for e in sortList:
				if e.endswith(' D') is True:
					# This element sorting is descending
					querySorting.append((e.strip(' D'),'desc'))
				else:
					# This element sorting is ascending
					if e.endswith(' A') is True:
						querySorting.append((e.strip(' A'),'asc'))
					else:
						querySorting.append((e,'asc'))

		return querySorting


	########################
	##  IGeoCollection overwriting
	########################
	def geoItems(self):
		"""Return georeferenced items in the container """
		featuretypes=self.featuretypes.keys()
		return [i.getObject() for i in self.getFeatureTypeItems(featuretypes)[0]]

	def getBoundingBox(self):
		"""Get the bounding box of contained items as a tuple
		(minx, miny, maxx, maxy)."""
		featuretypes=self.featuretypes.keys()
		return bboxAsTuple(self.computeBoundingBoxListFT(featuretypes))

	########################
	##  WFS processing
	########################
	def getFeatureTypeItems(self, ListFTname, bbox=None, filter=None, maxItems=None, sortBy=None):
		
		errorMessage=''
		items=[]
				
		sortList=self.getQuerySorting(sortBy)
		
		for i in sortList:
			if i[0] not in self.getGeoCatalog().indexes():
				errorMessage='ERROR: sortBy element does not exist'
				
		if errorMessage=='':		
			if bbox==None and filter==None:
				#getFeatureTypeItems without bbox and filter
				items=self.getGeoCatalog().evalAdvancedQuery(Generic('featureType',ListFTname),sortList)
			
			elif filter==None:
				#getFeatureTypeItems with bbox
				#items=self.getGeoCatalog().evalAdvancedQuery(Generic('geometry',{'query':BoundingBox(bbox[0], bbox[1], bbox[2], bbox[3]),'geometry_operator':'within'}))
				advQuery=Generic('featureType',ListFTname)&Generic('geometry',{'query':bboxFromTuple(bbox),'geometry_operator':'intersects'})
				items=self.getGeoCatalog().evalAdvancedQuery(advQuery,sortList)
			
			elif bbox==None:
				#getFeatureTypeItems with filter
				List_Nodes=filter
				List_ChildNodes=List_Nodes[0]._get_childNodes()
				(advQuery, errorMessage)=self.buildCompleteQuery(List_ChildNodes,ListFTname)
				items=self.getGeoCatalog().evalAdvancedQuery(advQuery,sortList)
			
			elif bbox is not None and filter is not None:
				#FILTER QUERY
				List_Nodes=filter
				List_ChildNodes=List_Nodes[0]._get_childNodes()
				(advQuery, errorMessage)=self.buildCompleteQuery(List_ChildNodes,ListFTname)
				if errorMessage=='':
					#BBOX QUERY
					#query['Advanced']=query['Advanced']&Generic('geometry',{'query':BoundingBox(bbox[0], bbox[1], bbox[2], bbox[3]),'geometry_operator':'within'})
					advQuery=advQuery&Generic('geometry',{'query':bboxFromTuple(bbox),'geometry_operator':'within'})
					items=self.getGeoCatalog().evalAdvancedQuery(advQuery,sortList)
		
		if errorMessage=='' and maxItems is not None:
			if len(items)<=maxItems:
				return (items,errorMessage)
			else:
				#len(items)>maxItems
				return (items[0:maxItems],errorMessage)
			
		return (items,errorMessage)
			
	def buildSimpleFilter(self,List_Nodes,filter):
		""" build a Filter hmap from a nodes list provided by a xml document 
		    and return an error message ('' if there is not error)
		"""
		ErrorMessage=''
		logicalOperators=('AND','OR','NOT')
		generalComparisonOperators=('PropertyIsEqualTo','PropertyIsNotEqualTo','PropertyIsLessThan','PropertyIsGreaterThan','PropertyIsLessThanOrEqualTo','PropertyIsGreaterThanOrEqualTo')
		arithmeticOperators=('Add','Sub','Mul','Div')
		numericTypes=('integer','float')
		filter['ArithmeticOperator']=None		
		
		List_ChildNodes=List_Nodes._get_childNodes()
					
		if List_Nodes.tagName not in logicalOperators:
			# Simple Filter
			filter['FilterType']=List_Nodes.tagName
			
			if List_Nodes._get_localName() == 'FeatureId':
				filter['FilterType'] = 'PropertyIsEqualTo'
				filter['PropertyName'] = 'id'
				filter['Literal'] = List_Nodes.getAttribute('fid')
				logger.info(filter['PropertyName']+' = '+filter['Literal'])
			elif List_Nodes.tagName=='PropertyIsNull':
				if len(List_ChildNodes)==1:
					theChildNode=List_ChildNodes[0]
					if theChildNode.tagName=='PropertyName':
						filter['PropertyName']=theChildNode.childNodes[0].nodeValue 
					else:
						ErrorMessage='ERROR : TAG CONSTRUCTION, This comparison operator must only contain PropertyName tag'
				else:
					ErrorMessage='ERROR : TAG CONSTRUCTION, This comparison operator must only contain PropertyName tag'
			
			elif List_Nodes.tagName=='PropertyIsBetween':
				if len(List_ChildNodes)==3:
					firstChildNode=List_ChildNodes[0]
					secondChildNode=List_ChildNodes[1]
					thirdChildNode=List_ChildNodes[2]
					if firstChildNode.tagName=='PropertyName' and secondChildNode.tagName=='LowerBoundary' and thirdChildNode.tagName=='UpperBoundary':
						filter['PropertyName']=firstChildNode.childNodes[0].nodeValue
						filter['LowerBoundary']=secondChildNode.childNodes[0].nodeValue
						filter['UpperBoundary']=thirdChildNode.childNodes[0].nodeValue
					else:
						ErrorMessage='ERROR : TAG CONSTRUCTION, This comparison operator must contain PropertyName, LowerBoundary and UpperBoundary tags'
				else:
					ErrorMessage='ERROR : TAG CONSTRUCTION, This comparison operator must contain PropertyName, LowerBoundary and UpperBoundary tags'

			elif List_Nodes.tagName in generalComparisonOperators: 
				if len(List_ChildNodes)==2: 
					#Retrieval of PropertyName and Literal Tags
					firstChildNode=List_ChildNodes[0]
					secondChildNode=List_ChildNodes[1]
					if str(firstChildNode.tagName)=='PropertyName' and str(secondChildNode.tagName)=='Literal':
						filter['PropertyName']=firstChildNode.childNodes[0].nodeValue
						filter['Literal']=secondChildNode.childNodes[0].nodeValue
					elif str(firstChildNode.tagName)=='PropertyName' and str(secondChildNode.tagName) in arithmeticOperators:
						filter['PropertyNameA']=firstChildNode.childNodes[0].nodeValue
						filter['ArithmeticOperator']=str(secondChildNode.tagName)
						littleChildNodes=secondChildNode._get_childNodes()
						filter['PropertyNameB']=littleChildNodes[0].childNodes[0].nodeValue
						filter['Literal']=littleChildNodes[1].childNodes[0].nodeValue
						if filter['PropertyNameA']==filter['PropertyNameB']:
							ErrorMessage='ERROR : ARITHMETIC CONSTRUCTION, The same element is used twice'
						if self.getElementType(filter['PropertyNameA']) not in numericTypes or self.getElementType(filter['PropertyNameB']) not in numericTypes:
							ErrorMessage='ERROR : ELEMENT TYPE, It is not possible to compare these elements (not numeric type)'
					else:
						ErrorMessage='ERROR : TAG CONSTRUCTION, This comparison operator must contain PropertyName and Literal tags or PropertyName and Arithmetic tags'
				else:
					ErrorMessage='ERROR : TAG CONSTRUCTION, This comparison operator must contain PropertyName and Literal tags'
			
			else :
				ErrorMessage='The accepted comparison operators are : PropertyIsEqualTo, PropertyIsNotEqualTo, PropertyIsLessThan, PropertyIsGreaterThan, PropertyIsLessThanOrEqualTo, PropertyIsGreaterThanOrEqualTo, PropertyIsNull, PropertyIsBetween'
			
			return ErrorMessage
		
	def applyComparisonOperator(self,filter,ListFTname):
		""" return a query built from a simple filter (Hmap) with comparison operator
		"""
		query=None
		filterType=filter['FilterType']
		
		if filter['ArithmeticOperator']==None:	
			# Only one feature type is considered	
			element=filter['PropertyName']
			if filterType=='PropertyIsEqualTo':
				query=Eq(str(element),self.stringConversionType(filter['Literal'],self.getElementType(element)))
			elif filterType=='PropertyIsLessThanOrEqualTo':
				maxValue=self.stringConversionType(filter['Literal'],self.getElementType(element))
				query=Le(str(element),maxValue)
			elif filterType=='PropertyIsGreaterThanOrEqualTo':
				minValue=self.stringConversionType(filter['Literal'],self.getElementType(element))
				query=Ge(str(element),minValue)
			elif filterType=='PropertyIsBetween':
				minValue=self.stringConversionType(filter['LowerBoundary'],self.getElementType(element))
				maxValue=self.stringConversionType(filter['UpperBoundary'],self.getElementType(element))
				query=Between(str(element),minValue,maxValue)
			elif filterType=='PropertyIsNull':
				query=Eq(str(element),None)
			elif filterType=='PropertyIsNotEqualTo':
				query=~Eq(str(element),self.stringConversionType(filter['Literal'],self.getElementType(element)))
			elif filterType=='PropertyIsLessThan':	
				maxValue=self.stringConversionType(filter['Literal'],self.getElementType(element))
				query=~Eq(str(element),maxValue)&Le(str(element),maxValue)
			elif filterType=='PropertyIsGreaterThan':	
				minValue=self.stringConversionType(filter['Literal'],self.getElementType(element))
				query=~Eq(str(element),minValue)&Ge(str(element),minValue)
		
		else:
			# Comparison and arithmetic operators
			query=self.applyArithmeticOperator(filter,ListFTname)
		
		return query
	
	
	def applyArithmeticOperator(self,filter,ListFTname):
		""" return a query built from a simple filter (Hmap) with comparison and arithmetic operators such as
			filter['PropertyNameA'] COMPARISON_OPERATOR filter['PropertyNameB'] ARITHMETIC_OPERATOR filter['Literal']
		"""
		query=None
		
		# Operator Determination
		if filter['ArithmeticOperator']=='Add':
			op="+"
		elif filter['ArithmeticOperator']=='Sub':
			op="-"
		elif filter['ArithmeticOperator']=='Mul':
			op="*"
		elif filter['ArithmeticOperator']=='Div':
			op="/"
		
		valB=[getattr(o,filter['PropertyNameB']) for o in self.getFeatureTypeItems(ListFTname)[0]]
		
		l=[(i,eval('i'+op+"self.stringConversionType(filter['Literal'],self.getElementType(filter['PropertyNameB']))")) for i in valB]
		
		queryComp=[]
		
		for v in l:
			filterComp={}
			filterComp['ArithmeticOperator']=None
			filterComp['FilterType']=filter['FilterType']
			filterComp['PropertyName']=filter['PropertyNameA']
			filterComp['Literal']=v[1]
			queryComp.append(Eq(filter['PropertyNameB'],v[0])& self.applyComparisonOperator(filterComp,ListFTname))
		
		query=Or(*[q for q in queryComp])
		
		return query
	

	
	def buildQuery(self,ANode,ListFTname):
		""" return the query built from a nodes List, provided by a xml document, containing only ONE logical operator 
		"""
		advanced=None
		op=None
		FilterError=''
						
		if ANode.tagName=='AND':
			
			op="And"
			
		elif ANode.tagName=='OR': 	
			
			op="Or"	
			
		if op=="And" or op=="Or":
			List_ChildNodes=ANode._get_childNodes()
			queryComp=[]		
			for n in List_ChildNodes:
				filter={}
				FilterError=self.buildSimpleFilter(n, filter)
				if FilterError=='':
					queryComp.append(self.applyComparisonOperator(filter,ListFTname))
					advanced=eval(op+'(*[q for q in queryComp])')
					
		elif ANode.tagName=='NOT':			
			List_ChildNodes=ANode._get_childNodes()
					
			for n in List_ChildNodes:
				filter={}
				FilterError=self.buildSimpleFilter(n, filter)
				if FilterError=='':
					simpleQuery=self.applyComparisonOperator(filter,ListFTname)
					if advanced==None:
						advanced=~simpleQuery
					else:
						advanced=advanced&~simpleQuery
				
		else:
			# NO LOGICAL OPERATOR
			filter={}
			FilterError=self.buildSimpleFilter(ANode, filter)
			if FilterError=='':
					advanced=self.applyComparisonOperator(filter,ListFTname)
					
		return (advanced, FilterError)

	
	def buildCompleteQuery(self,List_ChildNodes,ListFTname):
		""" return the complete query built from a nodes List provided by a xml document
		"""		
		error=''
		query=None
		logicalOperators=('AND','OR','NOT')
				
		if List_ChildNodes[0].tagName not in logicalOperators:
			# the filter doesn't contain logical operators
			(filterQuery,error)=self.buildQuery(List_ChildNodes[0],ListFTname)
		else:
			# the filter contains at least one logical operator 
			List_LittleChildNodes=List_ChildNodes[0]._get_childNodes()
			childTag=[i.tagName for i in List_LittleChildNodes]
			childLogicalTag=[t for t in childTag if t in logicalOperators]
			if childLogicalTag==[]:
				# Only one logical operator
				(filterQuery,error)=self.buildQuery(List_ChildNodes[0],ListFTname)  
			else:
				# Several logical operators
				queryComp=None
				# principal logical operator
				if List_ChildNodes[0].tagName=='AND':
					principalOp="&"
					(filterQuery,error)=self.buildQuery(List_LittleChildNodes[0], ListFTname)
				elif List_ChildNodes[0].tagName=='OR':
					principalOp="|"
					(filterQuery,error)=self.buildQuery(List_LittleChildNodes[0], ListFTname)
				elif List_ChildNodes[0].tagName=='NOT':
					principalOp="&~"
					(filterQuery,error)=self.buildQuery(List_LittleChildNodes[0], ListFTname)
					if error=='':
						filterQuery=~filterQuery
						
				if error=='':
					for n in List_LittleChildNodes[1:len(List_LittleChildNodes)]:		
						(queryComp,error)=self.buildQuery(n, ListFTname)
						if error=='':
							filterQuery=eval('filterQuery'+principalOp+'queryComp')
			
		if error=='':
			query=Or(*[Eq('featureType',str(ft)) for ft in ListFTname])&filterQuery
		
		return (query,error)
			
		
		
		
	########################
	##  Spatial processing
	########################
	def getFeatureTypeBoundingBox(self, ftname):
		if ftname in self.featuretypes:
			if self.featuretypes[ftname]['boundingbox'] is None:
				return None
			else:
				t = self.featuretypes[ftname]['boundingbox']
				if len(t)==2:
					return bboxFromTuple((t[0], t[1], t[0], t[1]))
				if len(t)==4:
					return bboxFromTuple(t)
		return None
		
	def computeFeatureTypeBoundingBox(self, ftname):
		""" compute entirely the BBOX
		"""
		(items, error) = self.getFeatureTypeItems(ftname)
		ft_dict=self.getFeatureTypesDict()
		if ftname in ft_dict:
			bbox = self.computeBoundingBox(items)
			if bbox is None:
				ft_dict[ftname]['boundingbox'] = None
			else:
				ft_dict[ftname]['boundingbox'] = bboxAsTuple(bbox)
			self.updateFeatureTypesDict(ft_dict)
			
	def refreshFeatureTypeBoundingBox(self, ftname, geom):
		""" update BBOX if geom not contained
		"""
		if geom is not None:
			ft_dict=self.getFeatureTypesDict()
			if ftname in ft_dict:
				bbox = self.getFeatureTypeBoundingBox(ftname)
				if bbox is None:
					#bbox = geom.envelope()
					bbox = geom.envelope
				elif geom.within(bbox)==0:
					#bbox = bbox.union(geom).envelope()
					bbox = bbox.union(geom).envelope
				ft_dict[ftname]['boundingbox'] = bboxAsTuple(bbox)
				self.updateFeatureTypesDict(ft_dict)
			
		
	def computeBoundingBox(self, items):
		bbox = None
		for i in items:
			if hasattr(i, 'geometryAsWKT') and getattr(i, 'geometryAsWKT') is not None:
				#geom = i.geometry
				geom = wkt.loads(i.geometryAsWKT)
				if geom is not None:
					if bbox is None:
						 #bbox = geom.envelope()
						bbox = geom.envelope
					else:
						if geom.within(bbox)==0:
							#bbox = bbox.union(geom).envelope()
							bbox = bbox.union(geom.envelope).envelope
		return bbox
	
	def computeBoundingBoxListFT(self, ListFTname):
		"""
		"""
		total_bbox=None
		for FT in ListFTname:
			bbox=self.getFeatureTypeBoundingBox(FT)
			if total_bbox is None:
				total_bbox = bbox
			else:
				if bbox is not None:
					total_bbox=total_bbox.union(bbox).envelope
		return total_bbox
			
	########################
	##  Configuration management
	########################
	
	def addFeatureType(self, ftname):
		"""
		"""
		ft_dict=self.getFeatureTypesDict()
		if not ftname in ft_dict:
			ft_dict[ftname] = {'elements': 
								{'Title': 'string'},
							'boundingbox':
								None
							}
			self.updateFeatureTypesDict(ft_dict)
		
	def removeFeatureTypes(self, ft_list):
		"""
		"""
		ft_dict=self.getFeatureTypesDict()
		for ftname in ft_list:
			if ftname in ft_dict:
				del ft_dict[ftname]
		self.updateFeatureTypesDict(ft_dict)
		
	def addElementToFeatureType(self, ftname, elem, type):
		"""
		"""
		ft_dict=self.getFeatureTypesDict()
		if ftname in ft_dict:
			elements = ft_dict[ftname]['elements']
			elements[elem]=type
			ft_dict[ftname]['elements']=elements
			self.updateFeatureTypesDict(ft_dict)
			self.getGeoCatalog().declareFTElement(elem, type)
		
	def removeElementsFromFeatureType(self, ftname, elem_list):
		"""
		"""
		ft_dict=self.getFeatureTypesDict()
		
		# collect all elements from other FT to check if catalog index and columns can be removed
		otherelements = []
		for f in ft_dict.keys():
			if f != ftname:
				for e in ft_dict[f]['elements'].keys():
					otherelements.append(e)
				
		if ftname in ft_dict:
			elements = ft_dict[ftname]['elements']
			for elem in elem_list:
				if elem in elements:
					del elements[elem]
					if not elem in otherelements:
						self.getGeoCatalog().removeFTElement(elem)
						
			ft_dict[ftname]['elements']=elements
			self.updateFeatureTypesDict(ft_dict)

