==================
CroppingImageField
==================

This will resize all images to the dimensions you specify,
but instead of stretching, it will scale the images and crop the overhang.

For some examples how to configure CroppingImageField and result pictures
see `<docs/examples.txt>`_ or the Project page on http://plone.org/products/cropping-imagefield


To use the field::

  from croppingimage.field import CroppingImageField

  CroppingImageField(
      name = 'image',
      long_edge_size = 600,
      short_edge_size = 450,

      # use this if you don't want portrait images to scale to (450x600) (see docs/examples.txt)
      force_format = 'landscape',

      sizes= {'large'  : (600, 450),
              'medium' : (300, 225),
              'thumb'  : (125,  94),},
      widget = ImageWidget(label= "Image",)


This will create an attribute called "image" with the sizes thumb, medium, large as given.

This will be accessible as object/image, and the sizes as:

* object/image_thumb
* object/image_medium
* object/image_large




Copyright/ Author/ Licence
==========================

copyright
  Sharkbyte Studios Ltd

author
  Ben Mason <ben@sharkbyte.co.uk>

contributions
   Harald Friessnegger 'fRiSi': eggification, force_format extension

license
   This software is under a GPL License. See separate file LICENSE.txt
