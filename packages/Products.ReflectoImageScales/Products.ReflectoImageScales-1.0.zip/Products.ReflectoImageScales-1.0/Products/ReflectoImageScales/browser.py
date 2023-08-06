from Products.ATContentTypes.content import image
from zope.publisher.interfaces import IPublishTraverse
from Products.Five.browser import BrowserView
from ZPublisher.BaseRequest import DefaultPublishTraverse
from App.Common import rfc1123_date
from Products.CMFCore.utils import getToolByName
import time
from stat import ST_MTIME

from cStringIO import StringIO
import PIL.Image

PIL_ALGO = PIL.Image.ANTIALIAS
PIL_QUALITY = 88

SIZES = image.ATImageSchema['image'].sizes


class ImageScaleTraverse(DefaultPublishTraverse):
    
    def publishTraverse(self, request, name):
        if name.startswith('image_') and self.context.Format().startswith('image/'):
            scale = ImageScaleView(self.context, request)
            scale.__name__ = name
            return scale.__of__(self.context)
        return super(ImageScaleTraverse, self).publishTraverse(request, name)


class ImageScaleView(BrowserView):

    def __call__(self):
        self.setCacheHeaders()
        scalename = self.__name__[len('image_'):]
        w, h = SIZES[scalename]
        thumbnail_file, format = scale(self.context.getFilesystemPath(), w, h)
        data = thumbnail_file.getvalue()
        format = 'image/%s' % format
        RESPONSE = self.request.RESPONSE
        RESPONSE.setHeader('Last-Modified', rfc1123_date(self.context.getStatus()[ST_MTIME]))
        RESPONSE.setHeader('Content-Type', format)
        RESPONSE.setHeader('Content-Length', len(data))
        return data
    
    def setCacheHeaders(self):
        # Custom cache header setting, as I can't get my head around cachefu
        mtool = getToolByName(self.context, 'portal_membership')
        if not mtool.isAnonymousUser():
            return
        ts = time.time() + 86400
        headers = {
            'cache-control': 'max-age=86400, s-maxage=86400, public, must-revalidate, proxy-revalidate',
            'expires': rfc1123_date(ts),
            'x-ReflectoImageScales': 'cache for 24h',
            }
        setHeader = self.request.RESPONSE
        for k, v in headers:
            setHeader(k, v)


def scale(path, w, h, default_format = 'PNG'):
    """ scale image (with material from ImageTag_Hotfix)"""
    #make sure we have valid int's
    size = int(w), int(h)

    original_file = open(path, 'rb')
    image = PIL.Image.open(original_file)
    # consider image mode when scaling
    # source images can be mode '1','L,','P','RGB(A)'
    # convert to greyscale or RGBA before scaling
    # preserve palletted mode (but not pallette)
    # for palletted-only image formats, e.g. GIF
    # PNG compression is OK for RGBA thumbnails
    original_mode = image.mode
    if original_mode == '1':
        image = image.convert('L')
    elif original_mode == 'P':
        image = image.convert('RGBA')
    image.thumbnail(size, PIL_ALGO)
    format = image.format and image.format or default_format
    # decided to only preserve palletted mode
    # for GIF, could also use image.format in ('GIF','PNG')
    if original_mode == 'P' and format == 'GIF':
        image = image.convert('P')
    thumbnail_file = StringIO()
    # quality parameter doesn't affect lossless formats
    image.save(thumbnail_file, format, quality=PIL_QUALITY)
    thumbnail_file.seek(0)
    return thumbnail_file, format.lower()


# Add some stuff to satisfy kupu
from Products.Reflecto.content.file import ReflectoFile

class FieldSizes(object):
    def getAvailableSizes(self, obj):
        return SIZES

def getField(self):
    pass

def getWrappedField(self, imagefield):
    return FieldSizes()

ReflectoFile.getField = getField
ReflectoFile.getWrappedField = getWrappedField
