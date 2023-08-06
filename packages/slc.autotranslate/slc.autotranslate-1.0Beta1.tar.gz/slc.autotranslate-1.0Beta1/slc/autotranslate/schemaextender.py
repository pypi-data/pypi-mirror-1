from zope.interface import implements

from archetypes.schemaextender.interfaces import ISchemaExtender
from archetypes.schemaextender.field import ExtensionField

from Products.Archetypes import atapi
from Products.CMFPlone import PloneMessageFactory as _

class ExtendedBooleanField(ExtensionField, atapi.BooleanField):
    """ """
 
class SchemaExtender(object):
    """ Extend a file to add the 'Auto-translate checkbox' """
    implements(ISchemaExtender)

    def __init__(self, context):
        self.context = context

    _fields = [
            ExtendedBooleanField('autoTranslateFlashUploadedFiles',
                schemata='settings',
                languageIndependent=True,
                widget=atapi.BooleanWidget(
                    label = _(
                        u'label_auto_translate_content', 
                        default=u'Automatically translate flash uploaded content?',
                    ),
                    description=_(
                        u'description_auto_translate_content', 
                        default=u"By selecting this option, specially named " +
                        "files, either starting or ending with a language " +
                        "code ('en', 'de', etc) and followed or preceded by " +
                        "an underscore, that are uploaded via the 'upload'" + 
                        "tab, will be automatically translated into that " +
                        "language."
                    ),
                ),
            ),
            ]

    def getFields(self):
        """ get fields """
        return self._fields


