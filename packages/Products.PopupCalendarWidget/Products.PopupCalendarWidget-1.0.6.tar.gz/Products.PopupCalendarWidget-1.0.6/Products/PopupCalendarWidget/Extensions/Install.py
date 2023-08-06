from StringIO import StringIO
from Products.Archetypes.public import listTypes
from Products.Archetypes.Extensions.utils import installTypes, install_subskin
from Products.CMFCore.utils import getToolByName
from OFS.ObjectManager import BadRequestException

from Products.PopupCalendarWidget import config

def install(self):
    out = StringIO()

    install_subskin(self, out, config.GLOBALS)
    installTypes(self, out, listTypes(config.PROJECTNAME), config.PROJECTNAME)
    
    portal = getToolByName(self,'portal_url').getPortalObject()
    
    from Products.PopupCalendarWidget.config import STYLESHEETS
    portal_css = getToolByName(portal, 'portal_css')
    try:
        for stylesheet in STYLESHEETS:
            try:
                portal_css.unregisterResource(stylesheet['id'])
            except:
                pass
            defaults = {'id': '',
            'media': 'all',
            'enabled': True}
            defaults.update(stylesheet)
            portal_css.manage_addStylesheet(**defaults)
    except:
        # No portal_css registry
        pass

    print >> out, "Successfully installed %s." % config.PROJECTNAME
    return out.getvalue()
