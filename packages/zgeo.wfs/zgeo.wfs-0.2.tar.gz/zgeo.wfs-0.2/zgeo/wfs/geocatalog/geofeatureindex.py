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

from Products.PluginIndexes.common.UnIndex import UnIndex

from zgeo.wfs.interfaces import IWFSGeoItem
import logging
logger = logging.getLogger('WFSCatalog')

class GeoFeatureIndex(UnIndex):

	"""Index for geofeature attribute provided by IWriteGeoreferenced adapter
	"""

	__implements__ = UnIndex.__implements__

	meta_type="GeoFeatureIndex"

	query_options = ["query"]

	def index_object(self, documentId, obj, threshold=None):
		"""
		"""
		geoitem=IWFSGeoItem(obj)
		fields = self.getIndexSourceNames()
		res = 0
		for attr in fields:
			if hasattr(obj, attr):
				res += self._index_object(documentId, obj, threshold, attr)
			else :
				res += self._index_object(documentId, geoitem, threshold, attr)
		
		return res>0
	