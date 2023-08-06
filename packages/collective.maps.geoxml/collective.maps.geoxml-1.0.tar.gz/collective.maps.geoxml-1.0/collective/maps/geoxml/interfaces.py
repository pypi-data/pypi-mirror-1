from zope import schema
from zope.interface import Interface

from zope.app.container.constraints import contains
from zope.app.container.constraints import containers

from collective.maps.geoxml import geoxmlMessageFactory as _

# -*- extra stuff goes here -*-

class IGeoXml(Interface):
    """Contains KML file"""
