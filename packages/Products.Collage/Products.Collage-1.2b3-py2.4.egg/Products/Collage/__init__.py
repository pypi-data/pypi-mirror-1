# $Id: __init__.py 69384 2008-08-01 17:38:51Z glenfant $

from Products.Archetypes.atapi import listTypes, process_types

GLOBALS = globals()

from config import DEFAULT_ADD_CONTENT_PERMISSION, PROJECTNAME

# Make the skins available as DirectoryViews
#registerDirectory('skins', GLOBALS)

def initialize(context):
    from Products.Collage import content
    from Products.CMFCore import utils as cmfutils

    dummy = content # Keep pyflakes silent
    # initialize the content, including types and add permissions
    content_types, constructors, ftis = process_types(
        listTypes(PROJECTNAME),
        PROJECTNAME)

    cmfutils.ContentInit('%s Content' % PROJECTNAME,
                         content_types = content_types,
                         permission = DEFAULT_ADD_CONTENT_PERMISSION,
                         extra_constructors = constructors,
                         fti = ftis,
                         ).initialize(context)
