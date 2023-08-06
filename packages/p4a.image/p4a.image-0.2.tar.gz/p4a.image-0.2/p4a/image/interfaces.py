from zope import interface
from zope import schema

from p4a.fileimage import file as p4afile
from p4a.fileimage import image as p4aimage
#from p4a.image import genre  # don't think we want Genre

try:
    from zope.dublincore.interfaces import IDCDescriptiveProperties
except ImportError:
    from zope.app.dublincore.interfaces import IDCDescriptiveProperties
    

from zope.i18nmessageid import MessageFactory
_ = MessageFactory('plone4artists')

class IAnyImageCapable(interface.Interface):
    """
    Any aspect of image/content capable.
    """


class IPossibleImage(IAnyImageCapable):
    """
    All objects that should have the ability to be converted to some
    form of image should implement this interface.
    """


class IImageEnhanced(interface.Interface):
    """
    All objects that have their media features activated/enhanced
    should have this marker interface applied.
    """


class IImage(interface.Interface):
    """
    Objects which have image information.
    """
    title = schema.TextLine(
        title=_(u'Image Title'), required=False)
    description = schema.Text(
        title=_(u'Caption'), required=False)
    file = p4afile.FileField(
        title=_(u'File'), required=False)
    # XXX: Really need to get rid of the preferred dimensions in image_thumbnail! This is a remnant 
    #      of p4a.audio. This will cause problems with the aspect ration of the thumbnails!
    image_thumbnail = p4aimage.ImageField(
        title=_(u'Image Thumbnail'), required=False,
        preferred_dimensions=(400, 300))
    photographer = schema.TextLine(
        title=_(u'Photographer'), required=False)
    dateCreated = schema.Datetime(
        title=_(u'Date Created'), required=False)
    copyright = schema.TextLine(
        title=_(u'Copyright'), required=False)
    keywords = schema.List(
        title=_(u'Keywords'), required=False,
        default=[], missing_value=[],
        description=_(u'Enter a commas separated list of keywords'),
        value_type=schema.TextLine())
    location = schema.TextLine(
        title=_(u'Location'), required=False)
    city = schema.TextLine(
        title=_(u'City'), required=False)
    state = schema.TextLine(
        title=_(u'Province or State'), required=False)
    country = schema.TextLine(
        title=_(u'Country'), required=False)
    resUnit = schema.ASCIILine(
        title=_(u'Resolution Unit'), required=False, readonly=True)
    xRes = schema.ASCIILine(
        title=_(u'Horizontal Resolution (dpi)'), required=False,
        readonly=True)
    yRes = schema.ASCIILine(
        title=_(u'Vertical Resolution (dpi)'), required=False,
        readonly=True)
    comment = schema.Text(
        title=_(u'Comment'), required=False)
    cameraModel = schema.ASCIILine(
        title=_(u'Camera Model'), required=False, readonly=True)
    iso = schema.ASCIILine(
        title=_(u'ISO'), required=False, readonly=True)
    width = schema.Int(
        title=_(u'Width'), required=True, readonly=True)
    height = schema.Int(
        title=_(u'Height'), required=True, readonly=True)
    image_type = schema.ASCIILine(
        title=_(u'Image Type'), required=True, readonly=True)
    gpsLat = schema.ASCIILine(
        title=_(u'GPS Latitude'), required=False)
    gpsLong = schema.ASCIILine(
        title=_(u'GPS Longitude'), required=False)
    gpsAlt = schema.TextLine(
        title=_(u'GPS Altitude'), required=False)


class IImageDataAccessor(interface.Interface):
    """
    Image implementation accessor (ie jpeg, tiff, etc).
    """

    image_type = schema.TextLine(title=_(u'Image Type'), required=True, readonly=True)
    
    def load(filename):
        pass
    def store(filename):
        pass


class IPossibleImageContainer(IAnyImageCapable):
    """
    Any folderish entity that can be turned into an actual image 
    container.
    """


class IImageContainerEnhanced(interface.Interface):
    """
    Any folderish entity that has had it's IImageContainer features
    enabled.
    """


class IImageContainer(interface.Interface):
    """
    Folderish objects that have image information, typically representing an 
    image collection or slideshow."""
    
    title           = schema.TextLine(title=_(u'Title'), required=False)
    description     = schema.Text(title=_(u'Description'), required=False)
    photographer    = schema.TextLine(title=_(u'Photographer'), required=False)
    copyright       = schema.TextLine(title=_(u'Copyright'), required=False)
    # XXX what to do about image here?
    folder_image    = p4aimage.ImageField(title=_(u'Folder Image'),required=False,preferred_dimensions=(400, 300))
    dateCreated     = schema.TextLine(title=_(u'Date Created'), required=False)


class IImageProvider(interface.Interface):
    """
    Provide image.
    """
    
    image_items = schema.List(title=_(u'Image Items'),required=True,readonly=True)


class IBasicImageSupport(interface.Interface):
    """
    Provides certain information about image support.
    """

    support_enabled = schema.Bool(title=u'Image Support Enabled?',
                                  required=True,
                                  readonly=True)


class IImageSupport(IBasicImageSupport):
    """
    Provides full information about image support.
    """


class IMediaActivator(interface.Interface):
    """For seeing the activation status or toggling activation."""

    media_activated = schema.Bool(title=u'Media Activated',
                                  required=True,
                                  readonly=False)


# Make the image geospatially aware
# From http://svn.gispython.org/zope/zgeo.geographer/trunk/zgeo/geographer/interfaces.py
# XXX Do we want more? (IGeoCollectionSimple; IGeoreferenceable)
# Sean Gillies: "ideally, anything that implements IGeoItemSimple can be output
#   to desktop GIS, or served up as GeoRSS/KML for the web"

class IGeometry(interface.Interface):

    """
    A geometry property with a geographic or projected coordinate system.

    The spatial reference system is implicitly lat/long WGS84, aka EPSG:4326.
    """

    # TODO: geometries other than points
    type = schema.Choice(
        values=("Point",),  # Eventually add LineString, Polygon, etc.
        title=u"Geometry Type",
        description=u"The name of the geometry type. See "
        "http://code.google.com/apis/kml/documentation/kml_tags_21.html",
        required=False,
        default="Point",
        )

    coordinates = schema.Tuple(
        title=u"Geometry Coordinates",
        description=u"A sequence of coordinate tuples",
        value_type=schema.Tuple(title=u"Coordinates"),
        required=False,
        default=(),
        )


class IGeoItemSimple(IDCDescriptiveProperties):
    """
    A simple georeferenced object, analogous to an item in GeoRSS, or a
    KML placemark.

    See http://georss.org/simple.html for an explanation of the simple GeoRSS
    profile.

    IDCDescriptiveProperties defines 'title' and 'description'.
    """

    id = schema.Id(
        title=u"Identifier",
        description=u"Unique identifer for the item",
        required=True,
        )

    uri = schema.URI(
        title=u"URI",
        description=u"Uniform Resource Identifier",
        required=False,
        )

    geometry = schema.Object(
        IGeometry,
        title=u"Geometry",
        description=u"The item's geometry",
        required=False,
        default=None,
        )

    info = schema.Dict(
        title=u"Info Dictionary",
        description=u"Dictionary which provides the Python feature protocol",
        readonly=True,
        )
