CroppableImageField is a drop-in replacement for the Archetype field
ImageField. Includes support for:

* Generating cropped thumbnails so that a collection of images can
  have thumbnails with a common aspect ratio independent of their
  individual aspect ratios.

* Dynamic rescaling of the original image.

Cropping
========

To demonstrate this we create a content type that uses
CroppableImageField:

    >>> from ely.croppableimagefield import CroppableImageField
    >>> from Products.Archetypes.public import BaseContent, Schema, BaseSchema
    >>> class Image(BaseContent):
    ...     schema = BaseSchema + Schema ((
    ...         CroppableImageField(
    ...             'image',
    ...             sizes={
    ...                 'preview' : (128, 128),
    ...                 'icon'    :  (32, 32),
    ...                 'listing' :  (16, 16),
    ...                 },
    ...             cropped_scales=(
    ...                 'icon',
    ...                 'listing',
    ...                 )
    ...             ),
    ...         ))

and register it with Archetypes:

    >>> from Products.Archetypes.public import registerType
    >>> registerType(Image, 'ely.croppableimagefield')

    >>> from Products.Archetypes.public import process_types, listTypes
    >>> process_types(listTypes('ely.croppableimagefield'),
    ...                         'ely.croppableimagefield')
    ((<class 'Image'>,), (<function addImage ...


Now we can create a instance of this content type:

    >>> image = Image(portal)

and provide it with a photo:

    >>> from ely.croppableimagefield.tests.tests import ImageUpload
    >>> image.setImage(ImageUpload('IMG_0001.jpg'))

The original photo is in landscape format:

    >>> original = image.getImage()
    >>> original.width, original.height
    (200, 148)

However, as configured via ``cropped_scales``, the two thumbnails
"icon" and "listing" have been cropped into squares:

    >>> icon = image.getField('image').getScale(image, scale='icon')
    >>> icon.width, icon.height
    (32, 32)

    >>> listing = image.getField('image').getScale(image, scale='listing')
    >>> listing.width, listing.height
    (16, 16)

But not "preview". This thumbnail follows the default behaviour of
``ImageField`` and honours the aspect ratio of the original:

    >>> preview = image.getField('image').getScale(image, scale='preview')
    >>> preview.width, preview.height
    (128, 94)


For portrait images the crop can be taken from the top of an image or
the bottom. This is specified by the ``crop_location`` of the field.
The default it to crop from the top. This time lets crop from the
bottom:

    >>> from ely.croppableimagefield import CROP_BOTTOM
    >>> class ImageBottom(BaseContent):
    ...     schema = BaseSchema + Schema ((
    ...         CroppableImageField(
    ...             'image',
    ...             sizes={
    ...                 'icon'    :  (32, 32),
    ...                 },
    ...             cropped_scales=(
    ...                 'icon',
    ...                 ),
    ...             crop_location=CROP_BOTTOM,
    ...             ),
    ...         ))
    >>> registerType(ImageBottom, 'ely.croppableimagefield')

    >>> image = ImageBottom(portal)
    >>> image.setImage(ImageUpload('IMG_0002.jpg'))
    >>> icon = image.getField('image').getScale(image, scale='icon')
    >>> icon.width, icon.height
    (32, 32)

Or cropping from the middle:

    >>> from ely.croppableimagefield import CROP_MIDDLE
    >>> class ImageBottom(BaseContent):
    ...     schema = BaseSchema + Schema ((
    ...         CroppableImageField(
    ...             'image',
    ...             sizes={
    ...                 'icon'    :  (32, 32),
    ...                 },
    ...             cropped_scales=(
    ...                 'icon',
    ...                 ),
    ...             crop_location=CROP_MIDDLE,
    ...             ),
    ...         ))
    >>> registerType(ImageBottom, 'ely.croppableimagefield')

    >>> image = ImageBottom(portal)
    >>> image.setImage(ImageUpload('IMG_0002.jpg'))
    >>> icon = image.getField('image').getScale(image, scale='icon')
    >>> icon.width, icon.height
    (32, 32)


Rescaling
=========

The original image can be rescaled on the fly. Typically this would be
used to reduce the image to suit a particular context.

To demonstrate this we have an image that is 200 wide

    >>> image.setImage(ImageUpload('IMG_0001.jpg'))
    >>> original = image.getImage()
    >>> original.width, original.height
    (200, 148)

which we want to scale down to 160 wide

    >>> field = original.getField('image')
    >>> size = 160, 160
    >>> data = field.rescaleOriginal(original, size)
    >>> image.setImage(data)

    >>> original = image.getImage()
    >>> original.width, original.height
    (160, 118)

