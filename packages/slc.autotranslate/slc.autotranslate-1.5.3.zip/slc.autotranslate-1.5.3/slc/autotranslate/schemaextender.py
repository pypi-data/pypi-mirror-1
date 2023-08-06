from zope.interface import implements

from archetypes.schemaextender.interfaces import ISchemaExtender
from archetypes.schemaextender.field import ExtensionField

from Products.Archetypes import atapi
from Products.CMFPlone import PloneMessageFactory as _

class ExtendedBooleanField(ExtensionField, atapi.BooleanField):
    """ """

class ExtendedStringField(ExtensionField, atapi.StringField):
    """ """
 
class SchemaExtender(object):
    """ Extend a file to add the 'Auto-translate checkbox' """
    implements(ISchemaExtender)

    def __init__(self, context):
        self.context = context

    _fields = [
            ExtendedBooleanField('autoTranslateUploadedFiles',
                schemata='settings',
                languageIndependent=True,
                accessor='getAutoTranslateUploadedFiles',
                widget=atapi.BooleanWidget(
                    visible={'edit': 'visible', 'view': 'invisible'},
                    label = _(
                        u'label_auto_translate_content', 
                        default=u'Automatically translate uploaded files?',
                    ),
                    description=_(
                        u'description_auto_translate_content', 
                        default=u"By selecting this option, specially named "  
                        "files, either starting or ending with a language "  
                        "code ('en', 'de', etc) and followed (or preceded) by "  
                        "an underscore, that are uploaded via the 'upload'"   
                        "tab or when a new file or image is created, "  
                        "will be automatically translated into that language."
                    ),
                ),
            ),
            ExtendedBooleanField('ignoreDuplicateUploadedFiles',
                schemata='settings',
                languageIndependent=True,
                accessor='getIgnoreDuplicateUploadedFiles',
                widget=atapi.BooleanWidget(
                    visible={'edit': 'visible', 'view': 'invisible'},
                    label = _(
                        u'label_ignore_duplicate_uploaded_files', 
                        default=u'Ignore uploaded files that are duplicates of ' 
                                'existing files?',
                    ),
                    description=_(
                        u'description_auto_translate_content', 
                        default=u"If checked, an uploaded file that is "
                        "identified as the duplicate of an existing file in this "
                        "folder, will be ignored and dropped. If not checked, "
                        "the uploaded file will replace the existing file."
                        "<br/>"
                        "WARNING: This option can created unexpected results for users "
                        "who are not aware of it's purpose, please use wisely. "
                        "<br/>"
                        "PLEASE NOTE: This option is only applicable in case the"
                        "'Auto translate' option, shown above, has also been "
                        "checked."  
                    ),
                ),
            ),
            ExtendedStringField('customTranslationMatchingMethod',
                schemata='settings',
                languageIndependent=True,
                accessor='getCustomTranslationMatchingMethod',
                widget=atapi.StringWidget(
                    visible={'edit': 'visible', 'view': 'invisible'},
                    size = '60',
                    label = _(
                        u'label_custom_translation_matching_method', 
                        default=u'Use the following custom translation matching method',
                    ),
                    description=_(
                        u'description_custom_translation_matching_method', 
                        default=u"This option can be used to specify a custom "
                        "method for locating existing translations of an "
                        "uploaded file. The value must be the import path of a "
                        "python method, without the method name. For example: "
                        "<em>collective.myproduct.utils</em> "
                        "The method name and signature <b>must</b> be the same as the "
                        "original name:" 
                        "<em>get_translations(folder, file_obj, base_filename, file_ext)</em>."
                        "<br/>"
                        "PLEASE NOE: This option is only for application "
                        "developers and customizers. If you are unsure of the "
                        "purpose of this field, please ignore it. "
                        "<br/>"
                        "PLEASE NOTE: This option is only applicable in case the"
                        "'Auto translate' option, shown above, has also been "
                        "checked."  
                    ),
                ),
            ),
            ]

    def getFields(self):
        """ get fields """
        return self._fields


