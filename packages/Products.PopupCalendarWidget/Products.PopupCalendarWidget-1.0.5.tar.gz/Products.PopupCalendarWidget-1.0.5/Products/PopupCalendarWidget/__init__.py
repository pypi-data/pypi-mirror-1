from Globals import package_home
from Products.Archetypes import public as atapi
try:
    from Products.CMFCore import CMFCorePermissions
except ImportError:
    from Products.CMFCore import permissions as CMFCorePermissions
from Products.CMFCore import utils as cmf_utils
from Products.CMFCore.DirectoryView import registerDirectory
import config
import sys

import PopupCalendarWidget

registerDirectory(config.SKINS_DIR, config.GLOBALS)

def initialize(context):
    
    if config.DEMO_TYPE:
        import examples.PopupCalendarType

    types = atapi.listTypes(config.PROJECTNAME)
    content_types, constructors, ftis = atapi.process_types( types,
                                                             config.PROJECTNAME)
    cmf_utils.ContentInit( '%s Content' % config.PROJECTNAME,
                 content_types = content_types,
                 permission = CMFCorePermissions.AddPortalContent,
                 extra_constructors = constructors,
                 fti = ftis,
               ).initialize(context)
