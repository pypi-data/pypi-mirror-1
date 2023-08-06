from AccessControl import ClassSecurityInfo
from Products.Archetypes.Field import ImageField
from Products.Archetypes.Registry import registerField
from Products.CMFCore.permissions import ModifyPortalContent
from Products.Archetypes.Field import _marker
from Products.Archetypes.Field import HAS_PIL
from ZODB.POSException import ConflictError
from Products.Archetypes.debug import log_exc
import PIL.Image
from cStringIO import StringIO

CROP_TOP = 0
CROP_BOTTOM = 1
CROP_MIDDLE = 2


class CroppableImageField(ImageField):
    """
    """

    _properties = ImageField._properties.copy()
    _properties.update({
        'cropped_scales': [],
        'crop_location': CROP_TOP,
    })

    security = ClassSecurityInfo()

    security.declareProtected(ModifyPortalContent, 'crop')
    def crop(self, image, default_format='PNG'):
        """Return a cropped version of the given image.
        """
        image = PIL.Image.open(StringIO(image))
        original_mode = image.mode
        if original_mode == '1':
            image = image.convert('L')
        elif original_mode == 'P':
            image = image.convert('RGBA')
        width, height = image.size
        if width > height:
            # Landscape. Crop the middle of the image.
            dimension = height
            excess = width - dimension
            left = excess/2
            right = left + dimension
            upper, lower = 0, dimension
        else:
            # Portait. Crop the specified portion of the image.
            dimension = width
            if self.crop_location == CROP_TOP:
                left, right = 0, dimension
                upper, lower = 0, dimension
            elif self.crop_location == CROP_BOTTOM:
                left, right = 0, dimension
                upper, lower = height-dimension, height
            elif self.crop_location == CROP_MIDDLE:
                left, right = 0, dimension
                excess = height-dimension
                upper = excess/2
                lower = upper + dimension
            else:
                raise ValueError(self.crop_location)
        return image.crop((left, upper, right, lower))



    security.declarePrivate('scale_from_crop')
    def scale_from_crop(self, image, w, h, default_format = 'PNG'):
        """ scale image (with material from ImageTag_Hotfix)
        """
        image = image.copy()
        #make sure we have valid int's
        size = int(w), int(h)

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
        image.thumbnail(size, self.pil_resize_algo)
        format = image.format and image.format or default_format
        # decided to only preserve palletted mode
        # for GIF, could also use image.format in ('GIF','PNG')
        if original_mode == 'P' and format == 'GIF':
            image = image.convert('P')
        thumbnail_file = StringIO()
        # quality parameter doesn't affect lossless formats
        image.save(thumbnail_file, format, quality=self.pil_quality)
        thumbnail_file.seek(0)
        return thumbnail_file, format.lower()



    security.declareProtected(ModifyPortalContent, 'createScales')
    def createScales(self, instance, value=_marker):
        """creates the scales and save them
        """
        sizes = self.getAvailableSizes(instance)
        if not HAS_PIL or not sizes:
            return
        # get data from the original size if value is None
        if value is _marker:
            img = self.getRaw(instance)
            if not img:
                return
            data = str(img.data)
        else:
            data = value

        crop = self.crop(data)

        # empty string - stop rescaling because PIL fails on an empty string
        if not data:
            return

        filename = self.getFilename(instance)

        for n, size in sizes.items():
            if size == (0,0):
                continue
            w, h = size
            id = self.getName() + "_" + n
            __traceback_info__ = (self, instance, id, w, h)
            try:
                if n in self.cropped_scales:
                    imgdata, format = self.scale_from_crop(crop, w, h)
                else:
                    imgdata, format = self.scale(data, w, h)
            except (ConflictError, KeyboardInterrupt):
                raise
            except:
                if not self.swallowResizeExceptions:
                    raise
                else:
                    log_exc('scaling failed')
                    # scaling failed, don't create a scaled version
                    continue

            mimetype = 'image/%s' % format.lower()
            image = self.content_class(id, self.getName(),
                                     imgdata,
                                     mimetype
                                     )
            # nice filename: filename_sizename.ext
            #fname = "%s_%s%s" % (filename, n, ext)
            #image.filename = fname
            image.filename = filename
            # manually use storage
            delattr(image, 'title')
            self.getStorage(instance).set(id, instance, image,
                                          mimetype=mimetype, filename=filename)


    security.declareProtected(ModifyPortalContent, 'rescaleOriginal')
    def rescaleOriginal(self, value, size=None, **kwargs):
        """Rescales the original image to the given size. This can be
        used to dynamically set the size of the original image.

        ``size`` is a tuple of width and height.

        ``value`` must be an ``OFS.Image.Image`` instance.
        """
        if size is None:
            return ImageField.rescaleOriginal(self, value, **kwargs)
        data = str(value.data)
        w, h = size
        __traceback_info__ = (self, value, w, h)
        fvalue, format = self.scale(data, w, h)
        data = fvalue.read()
        return data


registerField(CroppableImageField,
              title='Croppable Image',
              description='A field that crops image scales.')


