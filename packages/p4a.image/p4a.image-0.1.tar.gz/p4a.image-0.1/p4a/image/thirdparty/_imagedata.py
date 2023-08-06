import mimetypes
import os
import logging

from PIL import Image

from zope.app.annotation import interfaces as annointerfaces
from zope import interface
from zope import datetime

from OFS import Image as ofsimage

from p4a.image import interfaces
from p4a.image.thirdparty import EXIF
from p4a.image.thirdparty import iptcinfo
from p4a.fileimage import utils as fileutils

marker = object()

logger = logging.getLogger('p4a.image')

# XXX fix this
def write_image_thumbnail(id3tags, image_thumbnail):
    size = image_thumbnail.get_size()
    mime_type = image_thumbnail.content_type
    desc = u''

    tempfilename = fileutils.write_to_tempfile(image_thumbnail)
    frame = frames.ImageFrame.create(frames.ImageFrame.FRONT_COVER, 
                                     tempfilename,
                                     desc)

    imgs = id3tags.getImages()
    if len(imgs) == 0:
        id3tags.frames.append(frame)
    else:
        # find the frame index of the first image so we can
        # replace it with our new image frame
        for i in id3tags.frames:
            if i == imgs[0]:
                index = id3tags.frames.index(i)
                id3tags.frames[index] = frame
                break

class ImageDataAccessor(object):
    interface.implements(interfaces.IImageDataAccessor)
    
    def __init__(self, context):
        self._filecontent = context

    @property
    def image_type(self):
        # Use the mime type?
        return self._filecontent.getContentType()
        #return 'JPEG'

    @property
    def _image(self):
        image = getattr(self, '__cached_image', None)
        if image is not None:
            return image
        self.__cached_image = interfaces.IImage(self._filecontent)
        return self.__cached_image

    @property
    def _image_data(self):
        annotations = annointerfaces.IAnnotations(self._filecontent)
        return annotations.get(self._image.ANNO_KEY, None)


    def _getValue(self, metadata_dict, key_name, default=''):
        '''
        Receive dictionary and key name and return value. If no 
        value, return default.
        '''
        try:
            return metadata_dict[key_name]
        except:
            return default


    def _getInfo(self, filename):
        '''
        Get metadata that all images have.  This includes mime type (from Zope) and
        the dimensions of the image (from PIL).
        '''

        self._image_data['mime_type'] = self._filecontent.getContentType()
        PILInfo = Image.open(filename)
        self._image_data['width'],self._image_data['height'] = PILInfo.size


    _iptc_map = {
        'object name': 'title',
        # caption  will be used as Plone's description
        'caption/abstract': 'description', 
        'by-line': 'photographer',
        # Is Terms-of-Use available?
        'copyright notice': 'copyright',
        # keywords returns a python list of keywords
        'keywords': 'keywords', 
        # location would be something like "Boston Harbor"
        'sub-location': 'location', 
        'city': 'city',
        'province/state': 'state',
        'country/primary location name': 'country',
        # This is the ISO Country code 
        # (See http://userpage.chemie.fu-berlin.de/diverse/doc/ISO_3166.html)
        'country/primary location code': 'isoCountryCode'}

    _iptc_defaults = {'keywords': []}

    def _getIPTC(self, filename):
        """
        Get IPTC metadata information. This is typically data that is stored 
        in the image by various means, after it is created.
        """
        try:
            IPTCInfo = iptcinfo.IPTCInfo(filename).data
        except:
            IPTCInfo = {}

        for dataset in iptcinfo.c_datasets.itervalues():
            value = self._getValue(
                IPTCInfo, dataset,
                self._iptc_defaults.get(dataset, marker))
            if value is not marker:
                self._image_data[
                    self._iptc_map.get(dataset, dataset)] = value

    def _setIPTC(self, filename):
        """
        Set IPTC metadata information from the user's edits.
        """
        pass #for now

    def _getEXIFInfo(self, filename):
        file_ = open(filename)
        try:
            return EXIF.process_file(file_)
        except (ValueError, KeyError, TypeError, AttributeError):
            logger.exception(
                'EXIF processing failed for %s' % self._filecontent)
            return

    def _getEXIF(self, filename):
        """
        Get EXIF metadata information.  This is typically data that is set by
        the camera.
        """
        EXIFInfo = self._getEXIFInfo(filename)
        if EXIFInfo is None:
            return

# XXX: We should get other EXIF info that might be interesting to photographers...
#      See photo.net as example. Also, verify that exposureTime, focalLength, fNumber
#      are properly calculated.
#        if 'EXIF ExposureTime' in EXIFInfo:
#            self._image_data['exposureTime']    = EXIFInfo['EXIF ExposureTime'].printable
#        if 'EXIF FocalLength' in EXIFInfo:
#            self._image_data['focalLength']     = EXIFInfo['EXIF FocalLength'].printable
#        if 'EXIF Flash' in EXIFInfo:
#            self._image_data['flash']           = EXIFInfo['EXIF Flash'].printable.replace(' (!)','')
#        if 'EXIF FNumber' in EXIFInfo:
#            nom,denom = EXIFInfo['EXIF FNumber'].printable.split('/')
#            self._image_data['fNumber']         = 'f/%sL' % str( float(nom) / float(denom) )

        if 'EXIF DateTimeOriginal' in EXIFInfo:
            try:
                self._image_data[
                    'dateCreated'] = datetime.parseDatetimetz(
                    EXIFInfo['EXIF DateTimeOriginal'].printable)
            except datetime.DateTimeError:
                logger.exception(
                    'Invalid date in EXIF for %s' % self._filecontent)
        
        if 'MakerNote ISOSetting' in EXIFInfo:
            self._image_data['iso']             = 'ISO ' + str(eval(EXIFInfo['MakerNote ISOSetting'].printable)[1])
        if 'Image Model' in EXIFInfo:
            self._image_data['cameraModel']     = EXIFInfo['Image Model'].printable
        if 'Image ResolutionUnit' in EXIFInfo:
            self._image_data['resUnit']         = EXIFInfo['Image ResolutionUnit'].printable
        if 'Image XResolution' in EXIFInfo:
            self._image_data['xRes']            = EXIFInfo['Image XResolution'].printable
        if 'Image YResolution' in EXIFInfo:
            self._image_data['yRes']            = EXIFInfo['Image YResolution'].printable

        if 'GPS GPSLatitudeRef' in EXIFInfo:
            gpsLatRef = EXIFInfo['GPS GPSLatitudeRef'].values
        if 'GPS GPSLatitude' in EXIFInfo:
            xCoordDeg,xCoordMin,xCoordSec = EXIFInfo['GPS GPSLatitude'].values
            xCoordSecParts = str(xCoordSec).split('/')
            xCoordSecDeg = '%.5f' % (float(xCoordSecParts[0]) / float(xCoordSecParts[1]))
            self._image_data['gpsLat'] = '''%s Deg %s' %s" %s''' % (xCoordDeg,
                                                                 xCoordMin,
                                                                 xCoordSecDeg,
                                                                 gpsLatRef)

        if 'GPS GPSLongitudeRef' in EXIFInfo:
            gpsLongRef = EXIFInfo['GPS GPSLongitudeRef'].values
        if 'GPS GPSLongitude' in EXIFInfo:
            yCoordDeg,yCoordMin,yCoordSec = EXIFInfo['GPS GPSLongitude'].values
            yCoordSecParts = str(yCoordSec).split('/')
            yCoordSecDeg = '%.5f' % (float(yCoordSecParts[0]) / float(yCoordSecParts[1]))
            self._image_data['gpsLong'] = '''%s Deg %s' %s" %s''' % (yCoordDeg,
                                                                  yCoordMin,
                                                                  yCoordSecDeg,
                                                                  gpsLongRef)

        if 'GPS GPSAltitudeRef' in EXIFInfo:
            gpsAltRef = EXIFInfo['GPS GPSAltitudeRef'].values
        if 'GPS GPSAltitude' in EXIFInfo:
            zCoordDeg,zCoordMin,zCoordSec = EXIFInfo['GPS GPSAltitude'].values
            zCoordSecParts = str(zCoordSec).split('/')
            zCoordSecDeg = '%.5f' % (float(zCoordSecParts[0]) / float(zCoordSecParts[1]))
            self._image_data['gpsAlt'] = '''%s Deg %s' %s" %s''' % (zCoordDeg,
                                                                 zCoordMin,
                                                                 zCoordSecDeg,
                                                                 gpsAltRef)

        if 'GPS GPSMapDatum' in EXIFInfo:
            self._image_data['GPSDatum'] = EXIFInfo['GPS GPSMapDatum'].values



    def _setEXIF(self, filename):
        '''
        Set EXIF metadata information from the user's edits.
        '''
        pass # for now

    def _loadThumbnail(self, filename):
        '''
        Use thumbnails for images the same way we use embedded images in audio files.
        Retrieve the thumbnail from the image if it exists, otherwise make one.
        Note that this sort of functionality comes with ATImage, but since we also
        want to handle ATFile, we add it here.
        '''
        EXIFInfo = self._getEXIFInfo(filename)
        if EXIFInfo is None:
            return

        if 'JPEGThumbnail' in EXIFInfo:
            thumb = EXIFInfo['JPEGThumbnail']
            mime_type = 'image/jpeg'
        elif 'TIFFThumbnail' in EXIFInfo:
            thumb = EXIFInfo['TIFFThumbnail']
            mime_type = 'image/tiff'
        else:
            thumb = None

        if 'title' in self._image_data:
            try:
                thumb_title = self._image_data['title']+' thumbnail'
            except TypeError:
                thumb_title = 'Thumbnail'
        else:
            thumb_title = 'Thumbnail'

        # XXX When no thumbnail is available, create one using PIL. 
        #     Should be derived from original image and saved in JPEG format.

        if thumb is not None:
            ext = mimetypes.guess_extension(mime_type) or '.jpg'
            kwargs = dict(id=os.path.basename(filename)+ext, 
                          title=thumb_title, 
                          file=thumb,
                          content_type=mime_type)
            image = ofsimage.Image(**kwargs)
            self._image_data['image_thumbnail'] = image 

    def _storeThumbnail(self, filename):
        '''
        XXX do we want to be able to store a new thumbnail in the image?
        Audio code is:
        # saving the image(s)
        if self._image.image_thumbnail is not None:
            write_image_thumbnail(id3tags, self._image.image_thumbnail)
        We will replace write_image_thumbnail with this method...
        Or should this be a function, not a method like write_image_thumbnail is?
        Note EXIF can only handle jpeg or tiff thumbnails
        '''
        pass

    def load(self, filename):
        '''
        Depending on the mime type, load metadata by calling different functions.
        XXX load is called on initial create and on edit
            sync_image_metadata -> _load_image_metadata -> load
        XXX this won't work properly until store is working too
        '''

        self._getInfo(filename)

        if self._image_data['mime_type'] in ['image/jpeg','image/tiff']:
            self._getIPTC(filename)
            self._getEXIF(filename)
            self._loadThumbnail(filename)
        else:
            # Unknown image type. Pass for now.
            # XXX What will happen when gifs or some other types are uploaded?
            pass

    def store(self, filename):
        """
        Depending on the mime type, store metadata by calling different functions.
        XXX will we need to set the encoding for EXIF or IPTC?  if so it should
        XXX be UTF_8_ENCODING - relevant audio code:
          id3tags.setTextEncoding(eyeD3.frames.UTF_8_ENCODING)
          id3tags.setTitle(self._image.title or u'')
        """
        if self._image_data['mime_type'] in ['image/jpeg','image/tiff']:
            self._setIPTC(filename)
            self._setEXIF(filename)
            #self._storeThumbnail(filename) XXX is this desireable?
        else:
            # Unknown image type. Pass for now.
            # XXX What will happen when gifs or some other types are uploaded?
            pass
