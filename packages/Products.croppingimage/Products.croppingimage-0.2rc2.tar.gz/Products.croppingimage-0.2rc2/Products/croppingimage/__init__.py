# Zope 2 imports

# Archetypes imports
from Products.Archetypes.public import process_types, listTypes

# CMF imports
from Products.CMFCore.DirectoryView import registerDirectory

# Plone imports
#from Products.CMFPlone import utils as plone_utils

# Standard library imports
#import os, os.path

# Product imports
from config import GLOBALS, PROJECTNAME, SKINS_DIR

registerDirectory(SKINS_DIR, GLOBALS)


def initialize(context):
    ##Import Types here to register them
    import croppingimage

    # If we put this import line to the top of module then
    # utils will magically point to Ploneboard.utils
    from Products.CMFCore import utils

    content_types, constructors, ftis = process_types(
        listTypes(PROJECTNAME),
        PROJECTNAME)

    # Assign an own permission to all content types
    # Heavily based on Bricolite's code from Ben Saller
    import permissions as perms

    allTypes = zip(content_types, constructors)
    for atype, constructor in allTypes:
        kind = "%s: %s" % (PROJECTNAME, atype.archetype_name)
        utils.ContentInit(
            kind,
            content_types      = (atype,),
            # Add permissions look like perms.Add{meta_type}
            permission         = getattr(perms, 'Add%s' % atype.meta_type),
            extra_constructors = (constructor,),
            fti                = ftis,
            ).initialize(context)
