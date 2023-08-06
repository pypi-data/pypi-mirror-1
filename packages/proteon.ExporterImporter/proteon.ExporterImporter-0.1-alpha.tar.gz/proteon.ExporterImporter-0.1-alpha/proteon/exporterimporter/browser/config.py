from zope.component import getUtility
from zope.formlib import form
from zope.interface import implements
from zope import interface
from zope.app.component.hooks import getSite
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.interfaces import IVocabularyFactory
from plone.app.form.validators import null_validator


from plone.app.controlpanel.form import ControlPanelForm
from OFS.SimpleItem import SimpleItem

from Products.CMFCore.utils import getToolByName

from proteon.exporterimporter import exporterimporterMessageFactory as _
from proteon.exporterimporter.interfaces import IExporterImporterManagement
from proteon.exporterimporter.content.importer.content_importer import ImportTool


class ExporterImporterConfigurationForm(ControlPanelForm):
    form_fields = form.Fields(IExporterImporterManagement)
    label = _(u"SQL Importer settings form")
    description = _(u"Setup options for the importing process")
    form_name = _(u"SQLImporter Settings")

    actions = ControlPanelForm.actions

    @form.action(_(u'label_startimport', default=u'Start import'), name='startimport')
    def handle_startimport_action(self, action, data):
        asite = getSite()
        mci_tool = getToolByName(asite, ImportTool.id)
        to_import=data.get("export_file_choice", None)
        if not to_import:
            self.status = _("Please choose one of the available exports from the dropdown below first")
            return
        started = mci_tool.start_import(to_import)
        if started:
            self.status = _("Importer successfuly started")
        else:
            self.status = _("An instance of Import tool is already running, please wait until it has finished.")
        return


class ExporterImporterConfiguration(SimpleItem):
    implements(IExporterImporterManagement)

    def _getMCITool(self):
        asite = getSite()
        return getToolByName(asite, ImportTool.id)

    def set_import_root_path(self, root_path):
        self._getMCITool().import_root_path = root_path
    def get_import_root_path(self):
        return self._getMCITool().import_root_path
    import_root_path = property(get_import_root_path, set_import_root_path)

    def set_export_file_or_folder_path(self, fof_path):
        self._getMCITool().fof_path = fof_path
    def get_export_file_or_folder_path(self):
        return self._getMCITool().fof_path
    export_file_or_folder_path = property(get_export_file_or_folder_path, set_export_file_or_folder_path)

    def set_export_file_choice(self, chosen_export):
        mci_tool = self._getMCITool()
        mci_tool.chosen_export = chosen_export
    def get_export_file_choice(self):
        try:
            return self._getMCITool().chosen_export
        except AttributeError:
            return None
    export_file_choice = property(get_export_file_choice, set_export_file_choice)




def form_adapter(context):
    return getUtility(IExporterImporterManagement, name='exporter_importer_config', context=context)
