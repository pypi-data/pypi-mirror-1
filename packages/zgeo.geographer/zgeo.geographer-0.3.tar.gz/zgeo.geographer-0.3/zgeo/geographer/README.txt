zgeo.geographer Package Readme
==============================

Overview
--------

The goal of zgeo.geographer is to standardize geographic location metadata.
This document will explain and exercise the zgeo.geographer interfaces and geo
location annotator.

Any object that implements zope.annotation.interfaces.IAttributeAnnotatable and
zgeo.geographer.interfaces.IGeoreferenceable can be adapted and geo-referenced.
The former marker is standard for Zope content objects, and the latter can be
easily configured via ZCML.

Tests
-----

Let's test with an example placemark, which provides both of the marker
interfaces mentioned above.

    >>> from zgeo.geographer.example import Placemark
    >>> placemark = Placemark()

Adapt it to IGeoreferenced

    >>> from zgeo.geographer.interfaces import IGeoreferenced
    >>> geo = IGeoreferenced(placemark)

Its properties should all be None

    >>> geo.type is None
    True
    >>> geo.coordinates is None
    True
    >>> geo.crs is None
    True

Now set the location geometry to type "Point" and coordinates 105.08 degrees
West, 40.59 degrees North using setGeoInterface()

    >>> geo.setGeoInterface('Point', (-105.08, 40.59))

A georeferenced object has "type" and "coordinates" attributes which should
give us back what we put in.

    >>> geo.type
    'Point'
    >>> geo.coordinates
    (-105.08, 40.590000000000003)
    >>> geo.crs is None
    True

An event should have been sent

    >>> from zope.component.eventtesting import getEvents
    >>> from zope.lifecycleevent.interfaces import IObjectModifiedEvent
    >>> events = getEvents(IObjectModifiedEvent)
    >>> len(events)
    1
    >>> events[0].object is placemark
    True

