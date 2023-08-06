import logging
from zope import event
from App.config import getConfiguration
from Products.CMFCore.utils import getToolByName
from Products.LinguaPlone.config import RELATIONSHIP
from Products.LinguaPlone.I18NBaseObject import AlreadyTranslated
from interfaces import AutoTranslatedFileEvent

log = logging.getLogger('slc.autotranslate/events.py')

def translate_flash_uploaded_file(evt):
    """ Event handler registered for FlashUploadEvent
    """
    file = evt.object
    translate_file(file)

def translate_added_file(file, evt):
    """ Event handler registered
    """
    translate_file(file)

def translate_file(file):
    parent = file.aq_parent 
    if not hasattr(parent, 'Schema'):
        return

    translate = parent.Schema().get('autoTranslateUploadedFiles').get(parent)
    if not translate:
        return 

    file_obj = file.getFile()
    if '.' in file_obj.filename:
        file_name, file_ext = file_obj.filename.split('.')
    else:
        file_name = file_obj.filename
        file_ext = None

    l = file_name.split('_')
    if len(l[0]) == 2:
        lang = l[0]
        base_file_name = '_'.join(l[1:])
    elif len(l[-1]) == 2:
        lang = l[-1]
        base_file_name = '_'.join(l[:-1])
    else:
        log.warn("File language could not be identified. Filename need to be "   
                 "prepended or appended with the language identifier, i.e "   
                 "en_factsheet.pdf' or 'factsheet_en.pdf'")
        return

    try:
        file.setLanguage(lang)
    except AlreadyTranslated:
        log.warn("File with name %s could not be set to language '%s,"
                "a translation in this this language already exists!" \
                % (base_file_name, lang))

    # See if there are any other translations of the file, and try to get the
    # canonical from the first match.
    can_lang = parent.getCanonicalLanguage()
    langtool = getToolByName(parent, 'portal_languages')
    all_langs = langtool.listAvailableLanguages()
    translations = []
    for langcode, langname in [(can_lang, 'dummy')] + all_langs:
        if langcode == lang or (langcode == can_lang and langname != 'dummy'):
            continue

        prefixed = '%s_%s' % (langcode, base_file_name)
        suffixed = '%s_%s' % (base_file_name, langcode)
        if file_ext is not None:
            prefixed += '.%s' % file_ext
            suffixed += '.%s' % file_ext

        for attr in (prefixed, suffixed):
            if hasattr(parent, attr):
                obj = getattr(parent, attr)
                translations.append(obj)

    canonical = translations and translations[0].getCanonical() or None

    for obj in translations:
        file.addReference(obj, RELATIONSHIP)
        
    if lang == can_lang:
        file.setCanonical()
        if canonical:
            canonical.addReference(file, RELATIONSHIP)

    file.invalidateTranslationCache()        

    if getConfiguration().debug_mode:
        language = langtool.getNameForLanguageCode(lang)
        if canonical:
            log.info('Canonical is %s' % str(canonical.absolute_url()))
        log.info('Translated uploaded file into %s' % language)

    event.notify(AutoTranslatedFileEvent(file))


