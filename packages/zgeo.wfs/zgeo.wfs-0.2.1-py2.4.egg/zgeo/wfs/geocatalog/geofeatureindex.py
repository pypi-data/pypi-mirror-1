#
# Copyright (c) 2008 Eric BREHAULT
# contact: eric.brehault@makina-corpus.org
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
	