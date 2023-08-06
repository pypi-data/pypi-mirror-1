from zope import interface
from p4a.image import interfaces
from p4a.subtyper.interfaces import (IPortalTypedDescriptor,
                                     IPortalTypedFolderishDescriptor)

class ImageDescriptor(object):
    interface.implements(IPortalTypedDescriptor)

    title = u'Image'
    description = u'Image-based media content'
    type_interface = interfaces.IImageEnhanced
    for_portal_type = 'File'

class AbstractImageContainerDescriptor(object):
    interface.implements(IPortalTypedFolderishDescriptor)

    title = u'Image Container'
    description = u'Container for holding Image-based media content'
    type_interface = interfaces.IImageContainerEnhanced

class FolderImageContainerDescriptor(AbstractImageContainerDescriptor):
    for_portal_type = 'Folder'

class BTreeFolderImageContainerDescriptor(AbstractImageContainerDescriptor):
    for_portal_type = 'LargePloneFolder'

class TopicImageContainerDescriptor(AbstractImageContainerDescriptor):
    for_portal_type = 'Topic'
