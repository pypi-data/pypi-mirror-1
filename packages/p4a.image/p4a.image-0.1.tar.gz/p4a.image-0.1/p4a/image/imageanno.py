from persistent.dict import PersistentDict
from zope import event
from zope import interface
from zope.app.annotation import interfaces as annointerfaces
from zope.app.event import objectevent
from p4a.image import interfaces
from p4a.fileimage import DictProperty

class ImageAnnotationAddedEvent(objectevent.ObjectEvent):
    """Annotations added to an object for image metadata.
    """

class AnnotationImage(object):
    """An IImage adapter designed to handle ATCT based content.
    """
    
    interface.implements(interfaces.IImage)

    ANNO_KEY = 'p4a.image.imageanno.AnnotationImage'

    def __init__(self, context):
        self.context = context
        annotations = annointerfaces.IAnnotations(context)
        self.image_data = annotations.get(self.ANNO_KEY, None)
        if self.image_data is None:
            self.image_data = PersistentDict()
            annotations[self.ANNO_KEY] = self.image_data
            event.notify(ImageAnnotationAddedEvent(self))

    title           = DictProperty(interfaces.IImage['title'],          'image_data')
    description     = DictProperty(interfaces.IImage['description'],    'image_data')
    photographer    = DictProperty(interfaces.IImage['photographer'],   'image_data')
    dateCreated     = DictProperty(interfaces.IImage['dateCreated'],    'image_data')
    width           = DictProperty(interfaces.IImage['width'],          'image_data')
    height          = DictProperty(interfaces.IImage['height'],         'image_data')
    copyright       = DictProperty(interfaces.IImage['copyright'],      'image_data')
    keywords        = DictProperty(interfaces.IImage['keywords'],       'image_data')
    location        = DictProperty(interfaces.IImage['location'],       'image_data')
    city            = DictProperty(interfaces.IImage['city'],           'image_data')
    state           = DictProperty(interfaces.IImage['state'],          'image_data')
    country         = DictProperty(interfaces.IImage['country'],        'image_data')
    resUnit         = DictProperty(interfaces.IImage['resUnit'],        'image_data')
    xRes            = DictProperty(interfaces.IImage['xRes'],           'image_data')
    yRes            = DictProperty(interfaces.IImage['yRes'],           'image_data')
    comment     = DictProperty(interfaces.IImage['comment'],    'image_data')
    cameraModel     = DictProperty(interfaces.IImage['cameraModel'],    'image_data')
    iso             = DictProperty(interfaces.IImage['iso'],            'image_data')
    file            = DictProperty(interfaces.IImage['file'],           'image_data')
    image_thumbnail = DictProperty(interfaces.IImage['image_thumbnail'],'image_data')
    image_type      = DictProperty(interfaces.IImage['image_type'],     'image_data')
    gpsLat          = DictProperty(interfaces.IImage['gpsLat'],         'image_data')
    gpsLong         = DictProperty(interfaces.IImage['gpsLong'],        'image_data')
    gpsAlt          = DictProperty(interfaces.IImage['gpsAlt'],         'image_data')


class AnnotationImageContainer(object):
    """
    An IImageContainer adapter designed to handle ATCT based image content.
    """

    interface.implements(interfaces.IImageContainer)

    ANNO_KEY = 'p4a.image.imageanno.AnnotationImageContainer'

    def __init__(self, context):
        self.context = context
        annotations = annointerfaces.IAnnotations(context)
        self.image_data = annotations.get(self.ANNO_KEY, None)
        if self.image_data is None:
            self.image_data = PersistentDict()
            annotations[self.ANNO_KEY] = self.image_data
            event.notify(ImageAnnotationAddedEvent(self))

    def set_title(self,v):
        self.context.setTitle(v)
    def get_title(self):
        return self.context.Title()
    title = property(get_title, set_title)

    def set_description(self,v):
        self.context.setDescription(v)
    def get_description(self):
        return self.context.Description()
    description = property(get_description, set_description)

    photographer = DictProperty(interfaces.IImageContainer['photographer'], 'image_data')
    copyright = DictProperty(
        interfaces.IImageContainer['copyright'], 'image_data')
    dateCreated = DictProperty(interfaces.IImageContainer['dateCreated'], 'image_data')
    #genre = DictProperty(interfaces.IImageContainer['genre'], 'image_data')
    folder_image = DictProperty(interfaces.IImageContainer['folder_image'], 'image_data')
