from zope import component
from zope import interface
from zope import schema
from p4a.image import interfaces

class IContextualImageSupport(interfaces.IBasicImageSupport):
    can_activate_image = schema.Bool(title=u'Can Activate Image',
                                     readonly=True)
    can_deactivate_image = schema.Bool(title=u'Can Deactivate Image',
                                       readonly=True)

class Support(object):
    """
    A view that returns certain information regarding p4acal status.
    """

    interface.implements(IContextualImageSupport)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        
    @property
    def support_enabled(self):
        """
        Check to make sure an IImageSupport utility is available and
        if so, query it to determine if support is enabled.
        """
        
        support = component.queryUtility(interfaces.IImageSupport)
        if support is None:
            return False

        return support.support_enabled

    @property
    def _basic_can(self):
        if not self.support_enabled:
            return False

        if not interfaces.IAnyImageCapable.providedBy(self.context):
            return False

        return True

    @property
    def can_activate_image(self):
        if not self._basic_can:
            return False
        
        mediaconfig = component.getMultiAdapter((self.context, self.request),
                                                name='media-config.html')
        return not mediaconfig.media_activated

    @property
    def can_deactivate_image(self):
        if not self._basic_can:
            return False
        
        mediaconfig = component.getMultiAdapter((self.context, self.request),
                                                name='media-config.html')
        return mediaconfig.media_activated
