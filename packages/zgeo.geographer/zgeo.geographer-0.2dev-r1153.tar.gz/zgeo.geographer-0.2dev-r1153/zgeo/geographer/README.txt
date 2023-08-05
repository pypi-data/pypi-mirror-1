zgeo.geographer Package Readme
==============================

Overview
--------

The goal of zgeo.geographer is to standardize geographic location metadata.
This document will explain and exercise the zgeo.geographer interfaces and geo
location annotator.

Here is the simple class we'll use to test annotation:

    >>> class Placemark(object):
    ...     pass

Make an instance

    >>> placemark = Placemark()

Turn on the annotation machinery

    >>> from zope.configuration.xmlconfig import XMLConfig
    >>> import zope.annotation
    >>> import zope.app.component
    >>> XMLConfig('meta.zcml', zope.app.component)()
    >>> XMLConfig('configure.zcml', zope.annotation)()

Setting its geographic location metadata is just a matter of marking it as
annotatable and adapting it to IGeoreferenced, which we'll do explicitly

    >>> from zope.annotation.interfaces import IAttributeAnnotatable
    >>> from zgeo.geographer.interfaces import IGeoreferenceable
    >>> from zope.interface import alsoProvides
    >>> alsoProvides(placemark, IAttributeAnnotatable, IGeoreferenceable)

    >>> from zgeo.geographer.geo import GeoreferencingAnnotator
    >>> geoitem = GeoreferencingAnnotator(placemark)

Now set the location geometry to type "Point" and coordinates 105.08 degrees
West, 40.59 degrees North using setGeoInterface()

    >>> geoitem.setGeoInterface('Point', (-105.08, 40.59))

A georeferenced object has "type" and "coordinates" attributes which should
give us back what we put in.

    >>> geoitem.type
    'Point'
    >>> geoitem.coordinates
    (-105.08, 40.590000000000003)
    >>> geoitem.crs is None
    True

