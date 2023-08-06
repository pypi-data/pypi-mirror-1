#
# Copyright (c) 2008 Eric BREHAULT
# contact: eric.brehault@makina-corpus.org
#
from zope.interface import Interface, Attribute
from zope.schema import Field, Text, URI, Dict

from zgeo.geographer.interfaces import IGeoCollection, IWriteGeoreferenced

# Marker interfaces. These are on the "for" side of a Zope3 adapter.

class IWebFeatureServiceable(Interface):

	"""Marks classes which can expose a WFS service
	"""

	
# Interfaces to be provided by adapters/browserviews.

class IWebFeatureService(IGeoCollection):

	"""An OGC Web Feature Service
	"""

	name = Field(
		title=u"Name",
		description=u"WFS service name",
		required=False,
		)
		
	title = Field(
		title=u"Title",
		description=u"WFS service title",
		required=False,
		)
		
	abstract = Text(
		title=u"Abstract",
		description=u"WFS service abstract",
		required=False,
		)
		
	onlineresource = URI(
		title=u"OnlineResource",
		description=u"Uniform Resource Identifier",
		required=False,
		)
		
	featuretypes = Dict(
		title=u"Feature types",
		description=u"Dictionary which provides the feature types names and their elements list",
		)
		
	srs = Field(
		title=u"SRS",
		description=u"Spatial reference system",
		required=False,
		)
	
class IWFSGeoItem(IWriteGeoreferenced):

	"""A georeferenced object exposable through WFS
	"""
	
class IWFSGeoreferencedEvent(Interface):
    """An event fired when georeferenced.
    """
    
    context = Attribute("The content object that was saved.")
	