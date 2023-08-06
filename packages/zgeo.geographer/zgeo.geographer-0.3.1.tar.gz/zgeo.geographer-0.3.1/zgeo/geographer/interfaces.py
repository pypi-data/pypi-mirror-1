from zope.interface import Attribute, Interface
from zope.deprecation import deprecated


class IGeoreferenceable(Interface):
    
    """Marks classes that may be annotated with georeferencing properties.
    """


class IGeoInterface(Interface):

    """Provides the Python geo interface.

    See http://trac.gispython.org/projects/PCL/wiki/PythonGeoInterface
    for details.
    """

    __geo_interface__ = Attribute("""Python Geo Interface""")


class IGeoreferenced(Interface):

    """A geographically referenced object.

    The spatial reference system is implicitly long, lat WGS84. Geometry types
    and coordinates shall follow the Python geo interface specification, which
    itself tracks the GeoJSON draft specification at http://geojson.org.
    """

    type = Attribute(
        """The name of the geometry type: 'Point', 'LineString', 'Polygon'"""
        )
    coordinates = Attribute("""A sequence of coordinate tuples""")
    crs = Attribute("""A coordinate reference system as a dict.
        The default is decimal degree longitude and latitude using the 
        WGS 1984 reference system.""")


class IWritableGeoreference(Interface):

    def setGeoInterface(type, coordinates, crs):
        """Set the geometry via the geo interface."""


class IWriteGeoreferenced(IGeoreferenced, IWritableGeoreference):
    """Supports read/write georeferencing.
    """


# TODO: deprecate the interfaces below. they really aren't needed. IGeoItem
# and IGeoCollection will be better implement in views of other packages.

class IGeometry(IGeoInterface):

    """A geometry property with a geographic or projected coordinate system.

    The spatial reference system is implicitly long, lat WGS84. Geometry types
    and coordinates shall follow the Python geo interface specification, which
    itself tracks the GeoJSON draft specification at http://geojson.org.
    """

    type = Attribute(
        'The name of the geometry type: "Point", "LineString", or "Polygon"'
        )

    coordinates = Attribute('A sequence of coordinate tuples')


class IGeoItem(IGeoInterface):

    """A simple georeferenced object, analogous to an entry in GeoRSS, or a
    KML placemark.
    """

    id = Attribute('Unique identifier for the item')

    properties = Attribute('Mapping of item properties')

    geometry = Attribute('An object that provides IGeometry (above)')



class IGeoCollection(IGeoInterface):

    """A collection of objects that provide IGeoItem, analogous to an Atom
    feed or a KML folder.
    """

    features = Attribute('Iterator over objects that provide IGeoItem')


deprecated(
    'IGeometry',
    'IGeometry will be removed from zgeo.geographer 1.0'
    )

deprecated(
    'IGeoItem',
    'IGeoItem will be removed from zgeo.geographer 1.0'
    )

deprecated(
    'IGeoCollection',
    'IGeoCollection will be removed from zgeo.geographer 1.0'
    )

