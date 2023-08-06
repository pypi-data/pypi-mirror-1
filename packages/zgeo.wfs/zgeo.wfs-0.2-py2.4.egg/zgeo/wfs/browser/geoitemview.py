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
		
