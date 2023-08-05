
from zope.interface import implements
from zope.component import adapts
from zope.annotation.interfaces import IAnnotations
from persistent.dict import PersistentDict
from zgeo.geographer.interfaces import IGeoreferenced
from zgeo.geographer.interfaces import IGeoreferenceable, IGeoreferencedEvent

import logging

logger = logging.getLogger('zgeo.geographer.geo')


class GeoreferencedEvent(object):
    """Event to notify that object has been georeferenced.
    """
    implements(IGeoreferencedEvent)
    
    def __init__(self, context):
        self.context = context


KEY = 'zgeo.geographer.georeference'

class GeoreferencingAnnotator(object):
    
    """Geographically annotate objects with metadata modeled after GeoJSON.
    See http://geojson.org.
    """
    implements(IGeoreferenced)
    adapts(IGeoreferenceable)

    def __init__(self, context):
        self.context = context
        annotations = IAnnotations(context)
        self.geo = annotations.get(KEY, None)
        if not self.geo:
            annotations[KEY] = PersistentDict()
            self.geo = annotations[KEY]
            self.geo['type'] = None
            self.geo['coordinates'] = None
            self.geo['crs'] = None

    @property
    def type(self):
        return self.geo['type']

    @property
    def coordinates(self):
        return self.geo['coordinates']

    @property
    def crs(self):
        return self.geo['crs']

    def setGeoInterface(self, type, coordinates, crs=None):
        self.geo['type'] = type
        self.geo['coordinates'] = coordinates
        self.geo['crs'] = crs

