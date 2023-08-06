# Standard library imports
from cStringIO import StringIO
from cgi import FieldStorage

# Zope3 imports
#from zope.interface import implements

# Zope2 imports
from AccessControl import ClassSecurityInfo
from ZPublisher.HTTPRequest import FileUpload

# CMF imports
#from Products.CMFCore.utils import getToolByName

# Archetypes imports
from Products.Archetypes.public import BaseContent, registerType

# Product imports
from schema import cropping_image_schema
from config import PROJECTNAME, CROPPING_IMAGE_TYPE, LONG_NAME, DESIRED_WIDTH, DESIRED_HEIGHT

import permissions as perms

# PIL imports
import PIL.Image


class CroppingImage(BaseContent):
    """An Image type that crops to specified dimensions.
    """

    security = ClassSecurityInfo()
    schema = cropping_image_schema
    meta_type = CROPPING_IMAGE_TYPE
    archetype_name = portal_type = LONG_NAME
    content_icon = 'image_icon.gif'


def _getFormat(filename):
    # Taken from PIL.Image.save, but adjusted because that code seems to be broken!
    ext = '.%s' % filename.split('.')[-1].lower()
    try:
        format = PIL.Image.EXTENSION[ext]
    except KeyError:
        PIL.Image.init()
        try:
            format = PIL.Image.EXTENSION[ext]
        except KeyError:
            #raise KeyError(ext) # unknown extension
            raise Exception(PIL.Image.EXTENSION)
    return format


registerType(CroppingImage, PROJECTNAME)
