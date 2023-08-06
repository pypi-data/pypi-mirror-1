import urllib

from zope import event
from zope import interface
from zope.formlib import form
from zope.app.form import browser as za_form_browser
from zope.cachedescriptors import property
from zope.app.event import objectevent
from zope.i18n import translate
from zope.i18nmessageid import MessageFactory

from Products.CMFCore import utils as cmfutils
from Products.statusmessages import interfaces as statusmessages_ifaces

from p4a.common import formatting
from p4a.fileimage.image._widget import ImageURLWidget

#from p4a.image import genre # XXX are we going to use?
from p4a.image import interfaces
from p4a.image.browser import media

_ = MessageFactory('plone4artists')

# XXX: IImageView needs to be modified to fit what is appropriate for images.
# XXX: Rocky says this module should be seriously refactored...

class IImageView(interface.Interface):
    """
    """
    def title():        pass


class ImageView(object):
    """
    """

    def __init__(self, context, request):
        self.image_info = interfaces.IImage(context)

        mime_type = unicode(context.get_content_type())

    def image_type(self):   return self.image_info.image_type
    # Use the title from metadata as plone title if it exists
    def title(self):        return self.image_info.title
    # Likewise for plone description (called caption in metadata)
    def description(self):  return self.image_info.description
    def photographer(self): return self.image_info.photographer
    def width(self):        return self.image_info.width
    def height(self):       return self.image_info.height
    def copyright(self):    return self.image_info.copyright
    def keywords(self):     return self.image_info.keywords
    def location(self):     return self.image_info.location
    def city(self):         return self.image_info.city
    def state(self):        return self.image_info.state
    def country(self):      return self.image_info.country
    def resUnit(self):      return self.image_info.resUnit
    def xRes(self):         return self.image_info.xRes
    def yRes(self):         return self.image_info.yRes
    def comment(self):      return self.image_info.comment
    def cameraModel(self):  return self.image_info.cameraModel
    def iso(self):          return self.image_info.iso
    # DMS => Degrees Minutes Seconds
    def gpsDMSLat(self):    return self.image_info.gpsLat
    def gpsDMSLong(self):   return self.image_info.gpsLong
    def gpsDMSAlt(self):    return self.image_info.gpsAlt

    def dateCreated(self):
        date = self.image_info.dateCreated
        if date is not None:
            return date.strftime('%d %B %Y - %H:%M')
        return ''

    # Also, produce the gps coords as degrees for easy linking
    # to these coordinates in Google Maps, Yahoo Maps, etc.
    def gpsDegLatStr(self):
        if self.image_info.gpsLat:
            latParts     = self.image_info.gpsLat.replace(' Deg','').replace('"','').replace("'",'').split(' ')
            negPos = 1
            if latParts[3] == 'S':
                negPos = -1
            gpsDegLatStr = '%.6f' % (negPos * ((float(latParts[0]) / 1) + (float(latParts[1]) / 60) + (float(latParts[2]) / 3600)))
            return gpsDegLatStr
        else:
            return None

    def gpsDegLongStr(self):
        if self.image_info.gpsLong:
            longParts     = self.image_info.gpsLong.replace(' Deg','').replace('"','').replace("'",'').split(' ')
            negPos = 1
            if longParts[3] == 'W':
                negPos = -1
            gpsDegLongStr = '%.6f' % (negPos * ((float(longParts[0]) / 1) + (float(longParts[1]) / 60) + (float(longParts[2]) / 3600)))
            return gpsDegLongStr
        else:
            return None


class ImagePageView(media.BaseMediaDisplayView):
    """
    Page for displaying image.
    """

    adapted_interface = interfaces.IImage
    media_field = 'file'

    form_fields = form.FormFields(interfaces.IImage)
    label = u'View Image Info'

    @property.Lazy
    def template(self):
        return self.index

    def has_contentlicensing_support(self):
        try:
            from Products import ContentLicensing
            ContentLicensing # pyflakes
        except ImportError, e:
            return False

        try:
            cmfutils.getToolByName(self.context, 'portal_contentlicensing')
        except AttributeError, e:
            return False

        return True


def applyChanges(context, form_fields, data, adapters=None):
    if adapters is None:
        adapters = {}

    changed = []

    for form_field in form_fields:
        field = form_field.field
        # Adapt context, if necessary
        interface = field.interface
        adapter = adapters.get(interface)
        if adapter is None:
            if interface is None:
                adapter = context
            else:
                adapter = interface(context)
            adapters[interface] = adapter

        name = form_field.__name__
        newvalue = data.get(name, form_field) # using form_field as marker
        if (newvalue is not form_field) and (field.get(adapter) != newvalue):
            changed.append(name)
            field.set(adapter, newvalue)

    return changed

class KeywordWidget(za_form_browser.TextWidget):
    """Split the value into a list by commas"""

    def _toFieldValue(self, input):
        value = super(KeywordWidget, self)._toFieldValue(input)
        if self.convert_missing_value and input == self._missing:
            return value
        return [i.strip() for i in value.split(',') if i.strip()]

    def _toFormValue(self, value):
        if value != self.context.missing_value:
            value = ', '.join(value)
        return super(KeywordWidget, self)._toFormValue(value)

class ImageEditForm(form.EditForm):
    """
    Form for editing image fields.
    """

    form_fields = form.FormFields(interfaces.IImage)
    form_fields['keywords'].custom_widget = KeywordWidget
    label = _(u'Edit Image Data')
    
    @form.action(_(u"Apply"), condition=form.haveInputWidgets)
    def handle_edit_action(self, action, data):
        changed = applyChanges(
            self.context, self.form_fields, data, self.adapters)
        if changed:
            attrs = objectevent.Attributes(interfaces.IImage, *changed)
            event.notify(
                objectevent.ObjectModifiedEvent(self.context, attrs)
                )
            # TODO: Needs locale support. See also Five.form.EditView.
            self.status = _(u"Successfully updated")
        else:
            self.status = _(u'No changes')
        statusmessages_ifaces.IStatusMessage(
            self.request).addStatusMessage(self.status, 'info')
        redirect = self.request.response.redirect
        return redirect(self.context.absolute_url()+'/view')


class ImageContainerEditForm(form.EditForm):
    """
    Form for editing image container fields.
    """

    form_fields = form.FormFields(interfaces.IImageContainer)
    label = _(u'Edit Image Container Data')

    @form.action(_(u"Apply"), condition=form.haveInputWidgets)
    def handle_edit_action(self, action, data):
        changed = applyChanges(
            self.context, self.form_fields, data, self.adapters)
        if changed:
            attrs = objectevent.Attributes(interfaces.IImageContainer, *changed)
            event.notify(
                objectevent.ObjectModifiedEvent(self.context, attrs)
                )
            # TODO: Needs locale support. See also Five.form.EditView.
            self.status = _(u"Successfully updated")
        else:
            self.status = _(u'No changes')
        redirect = self.request.response.redirect
        msg = urllib.quote(translate(self.status))
        redirect(self.context.absolute_url()+'/view?portal_status_message=%s' % msg)


class ImageContainerView(form.PageDisplayForm):
    """
    View for image containers.
    """
    adapted_interface = interfaces.IImageContainer

    form_fields = form.FormFields(interfaces.IImageContainer)
    label = _(u'View Image Container Info')

    @property.Lazy
    def template(self):
        return self.index

    @property.Lazy
    def image_info(self):
        return interfaces.IImageContainer(self.context)

    @property.Lazy
    def _image_items(self):
        provider = interfaces.IImageProvider(self.context)
        # cheating here by getting image properties we need by looking
        # up context attribute which isn't in the interface contract
        results = []
        for x in provider.image_items:
            aImage = x.context
            field = aImage.getImage()
            results.append(
                {'title': x.title,
                 'description': x.context.Description(),
                 'photographer': x.photographer,
                 'size': formatting.fancy_data_size(field.get_size()),
                 'icon': aImage.getIcon(),
                 'url': aImage.absolute_url()})
        return results
        
    def _imageurlwidget(self, image_item):
        field = interfaces.IImage['image_thumbnail'].bind(image_item)
        w = ImageURLWidget(field, self.request)
        return w()

    def image_items(self):
        return self._image_items
    
    def photographer(self):
        return self.image_info.photographer
        
    def dateCreated(self):
        return self.image_info.dateCreated

    def has_syndication(self):
        try:
            view = self.context.restrictedTraverse('@@rss.xml')
            return True
        except:
            # it's ok if this doesn't exist, just means no syndication
            return False

    def should_display_summary(self):
        #XXX add this if using genre:   or self.image_info.genre \
        return self.image_info.photographer \
               or self.image_info.dateCreated \
               or len(self._image_items) > 0

    def should_display_art(self):
        return self.image_info.image_thumbnail is not None
