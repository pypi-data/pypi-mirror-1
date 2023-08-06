###############
# Settings
###############

DESIRED_WIDTH  = 600
DESIRED_HEIGHT = 450

###############
# End Settings
###############

CROPPING_IMAGE_TYPE = 'CroppingImage'
LONG_NAME = 'Cropping Image'
PROJECTNAME = 'croppingimage'

SKINS_DIR = 'skins'

GLOBALS = globals()

from Globals import package_home
_product_dir = package_home(GLOBALS)
f = file('%s/version.txt' % _product_dir, 'r')
VERSION = f.read().strip()
f.close()

del f
del package_home
del _product_dir
