from cStringIO import StringIO

from zope.component import getSiteManager
from zope.interface import noLongerProvides

from Products.CMFCore.utils import getToolByName
from proteon.exporterimporter.config import PROJECTNAME

def uninstall(self, reinstall=False, out=None):
    if out is None:
        out = StringIO()
    if not reinstall:
        try:
            cptool = getToolByName(self, 'portal_controlpanel')
            cptool.unregisterConfiglet(PROJECTNAME)
            out.write('Removed %s Configlet' % PROJECTNAME)
        except:
            out.write('Failed to remove %s Configlet' % PROJECTNAME)
    return out.getvalue()
