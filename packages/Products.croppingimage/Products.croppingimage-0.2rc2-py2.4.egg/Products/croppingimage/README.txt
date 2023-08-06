CroppingImageField by Sharkbyte Studios Ltd
ben@sharkbyte.co.uk

This will resize all images to the dimensions you specify, but instead of stretching, it will scale the images and crop the overhang.

To use:

from croppingimage.field import CroppingImageField

CroppingImageField('image',
               required=True,
               primary=True,
               languageIndependent=True,
               long_edge_size = 600,
               short_edge_size = 450,
               sizes= {'large'  : (600, 450),
                       'medium' : (300, 225),
                       'thumb'  : (125,  94),
                      },
               validators = (('isNonEmptyFile', V_REQUIRED),
                             ('checkImageMaxSize', V_REQUIRED)),
               widget = ImageWidget(
                        description = "",
                        label= "Image",
                        label_msgid = "label_image",
                        i18n_domain = "plone",
                        show_content_type = False,))

This will create an attribute called "image" with the sizes thumb, medium, large as given. 

This will be accessible as object/image, and the sizes as:

  * object/image_thumb
  * object/image_medium
  * object/image_large
