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

from Products.ZCatalog.ZCatalog import ZCatalog
from Products.ZCatalog.Catalog import CatalogError
from Products.ZCatalog.ZCatalog import Catalog
from Missing import MV

from Products.PluginIndexes.FieldIndex.FieldIndex import FieldIndex

from Products.CMFCore.ActionProviderBase import ActionProviderBase
from Products.CMFCore.utils import UniqueObject

from zgeo.wfs.geocatalog.geometryindex import GeometryIndex
from zgeo.wfs.geocatalog.geofeatureindex import GeoFeatureIndex
from zgeo.wfs.interfaces import IWFSGeoItem

class GeoCatalog(UniqueObject, ZCatalog, ActionProviderBase):
	""" ZCatalog to index all the geo items
	"""
	
	def __init__(self,oid,**kw):
		"""
		"""
		ZCatalog.__init__(self, oid)
		self._catalog = GeoGMLCatalog()
		# indexes creation
		self._catalog.addIndex('featureType',GeoFeatureIndex('featureType'))
		self._catalog.addIndex('name',GeoFeatureIndex('name'))
		self._catalog.addIndex('geometry',GeometryIndex('geometry'))
		self.addIndex('id','FieldIndex')
		
		#metadata creation
		self.addColumn('getGML')
		self.addColumn('geometryAsWKT')
		self.addColumn('Title')
		self.addColumn('name')
		
	def declareFTElement(self, elementname, elementtype):
		"""
		"""
		# elementtype is useless at the moment, but will be used to choose the index type
		try:
			self.addIndex(elementname,'FieldIndex')
			self.addColumn(elementname)
			self.refreshCatalog()
		except CatalogError:
			#  already exists
			pass
		
	def removeFTElement(self, elementname):
		"""
		"""
		try:
			self.delIndex(elementname)
			self.delColumn(elementname)
			self.refreshCatalog()
		except CatalogError:
			# doesn't exist
			pass
		


try:
	from DocumentTemplate.cDocumentTemplate import safe_callable
except ImportError:
	# Fallback to python implementation to avoid dependancy on DocumentTemplate
	def safe_callable(ob):
		# Works with ExtensionClasses and Acquisition.
		if hasattr(ob, '__class__'):
			return hasattr(ob, '__call__') or isinstance(ob, types.ClassType)
		else:
			return callable(ob)

class GeoGMLCatalog(Catalog):
	"""(just overloads recordify method)
	"""

	def recordify(self, object):
		""" turns an object into a record tuple """
		geoitem=IWFSGeoItem(object)
		#geoitem=object
		record = []
		# the unique id is allways the first element
		for x in self.names:
			if hasattr(geoitem, x):
				attr=getattr(geoitem, x, MV)
			else:
				attr=getattr(object, x, MV)
				
			if(attr is not MV and safe_callable(attr)): attr=attr()
			record.append(attr)
		return tuple(record)