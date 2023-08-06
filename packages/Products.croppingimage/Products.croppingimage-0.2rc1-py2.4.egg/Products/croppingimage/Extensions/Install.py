# CMF imports
from Products.CMFCore.utils import getToolByName

# Standard library imports
from cStringIO import StringIO

# Archetypes imports
from Products.Archetypes.public import listTypes, process_types
from Products.Archetypes.Extensions.utils import installTypes, install_subskin

# Product imports
from Products.croppingimage.config import PROJECTNAME, GLOBALS


def install(self, reinstall=False):
    out = StringIO()

    the_types = listTypes(PROJECTNAME)
    installTypes(self, out, the_types, PROJECTNAME)
    types_as_str = ', '.join( [each['portal_type'] for each in the_types] )
    out.write( 'Installed the portal_types: %s\n' % types_as_str )

    install_subskin(self, out, GLOBALS)

    print >> out, "Successfully installed %s.\n" % PROJECTNAME
    return out.getvalue()

