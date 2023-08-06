# -*- extra stuff goes here -*-
from zope import schema
from zope.schema import ValidationError
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.interfaces import IContextSourceBinder
from zope.interface import Interface, implements
from zope.app.component.hooks import getSite

from Products.CMFCore.utils import getToolByName

from proteon.exporterimporter import exporterimporterMessageFactory as _
from proteon.exporterimporter.content.importer.content_importer import ImportTool

def get_available_exports():
    return

class PossibleImports(object):
    implements(IContextSourceBinder)

    def __call__(self, context):
        terms = []
        plone_site = getSite()
        asite = getSite()
        mctool = getToolByName(asite, ImportTool.id)
        terms = [(aexp, aexp) for aexp in mctool.getExports()]
        return SimpleVocabulary.fromItems(terms)

class InvalidPlonePath(ValidationError):
        "The path given is not a valid one in this plone instance."

def import_root_validator(value):
    site = getSite()
    try:
        clean_value = value
        if isinstance(clean_value, unicode):
            clean_value = value.encode("utf-8")
        import_from = site.restrictedTraverse(clean_value)
        is_valid_path = True
    except KeyError:
        raise InvalidPlonePath(value)
    else:
        if not import_from.absolute_url_path().startswith(site.absolute_url_path()):
            raise InvalidPlonePath(value)
    return is_valid_path


class IExporterImporterManagement(Interface):
    """
    """
    import_root_path= schema.TextLine(
        title = _(u"Import Root Path"),
        required = False,
        description = _(u"From where to begin the import, this is specially useful when doing partial imports."),
        constraint=import_root_validator
    )

    export_file_choice = schema.Choice(
        title = _(u"Which of these files should we import into this site?"),
        required = False,
        source=PossibleImports(),
        description = _(u"The available exports for this instance"),
    )

