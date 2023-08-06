
from zope.interface import implements
from zope.annotation.interfaces import IAttributeAnnotatable
from zgeo.geographer.interfaces import IGeoreferenceable


class Placemark(object):
    implements(IGeoreferenceable, IAttributeAnnotatable)

