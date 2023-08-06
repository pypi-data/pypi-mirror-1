Introduction
============

CroppableImageField is a drop-in replacement for the Archetype field
ImageField. Includes support for:

* Generating cropped thumbnails so that a collection of images can
  have thumbnails with a common aspect ratio independent of their
  individual aspect ratios. CroppableImageField lets you indicate
  which part of the image to crop from. You can configure
  CroppableImageField to crop from the top, middle or bottom of an
  image.

* Dynamic rescaling of the original image.

(Other cropping or clipping products already exist. All have slightly
varying features.)


Status
======

In use on several production sites.

