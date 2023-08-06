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
	