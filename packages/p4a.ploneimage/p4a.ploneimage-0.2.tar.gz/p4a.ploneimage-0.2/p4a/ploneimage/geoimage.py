from zope.interface import implements
from zope.app.annotation.interfaces import IAnnotations

from p4a.image.interfaces import IGeoItemSimple, IGeometry

from zope.component.factory import Factory
from zope.schema.fieldproperty import FieldProperty

# Geometry class and factory

class Geometry(object):

    """A simple geometry.
    """
    implements(IGeometry)

    type = FieldProperty(IGeometry['type'])
    coordinates = FieldProperty(IGeometry['coordinates'])

geometryFactory = Factory(
    Geometry,
    title=u'Create a new geometry property',
    )

class GeoImage(object):

    """An image adapter that proides geographic metadata
    """
    implements(IGeoItemSimple)

    def __init__(self, context):
        """Initialize adapter."""
        self.context = context

    @property
    def id(self):
        return self.id

    @property
    def uri(self):
        return self.uri

    @property
    def geometry(self):
        context = self.context
        return {
                'type': self.geometry.type,
                'coordinates': self.geometry.coordinates,
                }

    @property
    def info(self):
        GPSLatitude  = self.EXIFInfo['GPS GPSLatitude']
        GPSLongitude = self.EXIFInfo['GPS GPSLongitude']
        geofeature = "{'type': 'Point','coordinates': [[%s, %s]],}" % GPSLatitude , GPSLongitude
        return geofeature


