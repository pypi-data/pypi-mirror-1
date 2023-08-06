"""Definition of the GeoXml content type
"""

from zope.interface import implements, directlyProvides
from AccessControl import ClassSecurityInfo

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata

from collective.maps.geoxml import geoxmlMessageFactory as _
from collective.maps.geoxml.interfaces import IGeoXml
from collective.maps.geoxml.config import PROJECTNAME

GeoXmlSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

    atapi.IntegerField(
        name='zoom',
        vocabulary=range(0,20),
        default=0,
        storage = atapi.AnnotationStorage(),
        required=False,
        widget=atapi.SelectionWidget(
            label=_(u"zoom"),
            description=_(u"Initial zoom of map. (0: auto)"),
        ),
    ),

    atapi.StringField(
        name='mapType',
        vocabulary=['normal', 'satellite', 'hybrid'],
        default='normal',
        storage=atapi.AnnotationStorage(),
        required=False,
        widget=atapi.SelectionWidget(
            label=_(u"Map Type"),
            description=_(u"Choose a map type"),
        ),
    ),

     atapi.FileField(
        name='kml',
        storage = atapi.AnnotationStorage(),
        required=False,
        primary=True,
        widget=atapi.FileWidget(
            label=_(u"kml"),
            description=_(u"Add a kml file (Keyhole Markup Language)."),
        ),
    ),

))

GeoXmlSchema['title'].storage = atapi.AnnotationStorage()
GeoXmlSchema['description'].storage = atapi.AnnotationStorage()
schemata.finalizeATCTSchema(GeoXmlSchema, moveDiscussion=False)

class GeoXml(base.ATCTContent):
    """Contains KML file"""
    implements(IGeoXml)

    portal_type = "GeoXml"
    schema = GeoXmlSchema

    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')

    security = ClassSecurityInfo()

    security.declareProtected('View', 'download')
    def download(self, REQUEST=None, RESPONSE=None):
        """Download the kml file
        """
        if REQUEST is None:
            REQUEST = self.REQUEST
        if RESPONSE is None:
            RESPONSE = REQUEST.RESPONSE
        field = self.getPrimaryField()
        return field.download(self, REQUEST, RESPONSE)


atapi.registerType(GeoXml, PROJECTNAME)
