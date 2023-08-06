#
# Copyright (c) 2008 Eric BREHAULT
# contact: eric.brehault@makina-corpus.org
#

from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from zope import event
from Products.Archetypes.event import ObjectEditedEvent

from zgeo.geographer.interfaces import IWriteGeoreferenced

import logging
logger = logging.getLogger('WFSView')

class GeoItemView(BrowserView):
	""" View on a georeferenced object
	"""
	
	editgeometry_screen = ViewPageTemplateFile('editGeometry.pt')
	
	def __call__(self):
		"""
		"""
		logger.info("EDIT GEOM")
		action = self.request.get('ACTION')	
		if action=='STORE_GEOMETRY':
			logger.info("STORE GEOM")
			self.manage_storeGeometry()
		return self.editgeometry_screen()
			

	def getGeoInterface(self):
		"""
		"""
		adapted = IWriteGeoreferenced(self.context)
		return adapted.geo
		
	def manage_storeGeometry(self):
		"""
		"""
		type=self.request.get('geo_type')
		str_coords=self.request.get('geo_coords')
		IWriteGeoreferenced(self.context).setGeoInterface(type, eval(str_coords),crs="EPSG:4326")
		event.notify(ObjectEditedEvent(self.context))
		
