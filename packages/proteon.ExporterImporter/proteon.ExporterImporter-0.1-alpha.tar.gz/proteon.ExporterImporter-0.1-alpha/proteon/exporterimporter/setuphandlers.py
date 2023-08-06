from zope.component import getSiteManager
from Products.CMFCore.utils import getToolByName

from proteon.exporterimporter.interfaces import IExporterImporterManagement
from proteon.exporterimporter.browser.config import ExporterImporterConfiguration

from proteon.exporterimporter.config import PROJECTNAME
from proteon.exporterimporter.content.importer.content_importer import ImportTool

def install_utility(context):

    if context.readDataFile('proteon.exporterimporter_various.txt') is None:
        return

    portal = context.getSite()
    sm = getSiteManager()
    if not sm.queryUtility(IExporterImporterManagement, name='exporter_importer_config'):
        sm.registerUtility(ExporterImporterConfiguration(),
                        IExporterImporterManagement,
                           'exporter_importer_config')
    try:
        getToolByName(portal,ImportTool.id)
    except AttributeError:
        portal.manage_addProduct[PROJECTNAME].manage_addTool(ImportTool.id)
