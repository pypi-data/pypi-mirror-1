from zope.interface import implements
from zope.lifecycleevent.interfaces import IObjectModifiedEvent

class IObjectGeoreferencedEvent(IObjectModifiedEvent):
    """An event signaling that an object has been georeferenced
    """

class ObjectGeoreferencedEvent(object):
    implements(IObjectGeoreferencedEvent)

    def __init__(self, ob):
        self.object = ob
