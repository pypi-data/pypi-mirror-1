import logging

from zope import event
from zope.app.component.hooks import getSite

from App.config import getConfiguration
from OFS.CopySupport import CopyError

from Products.CMFCore.utils import getToolByName
from Products.LinguaPlone.config import RELATIONSHIP
from Products.LinguaPlone.I18NBaseObject import AlreadyTranslated
from Products.LinguaPlone.interfaces import ITranslatable

from interfaces import AutoTranslatedFileEvent

log = logging.getLogger('slc.autotranslate/utils.py')

def split_filename(filename):
    """ 
    Split the filename into it's language, name and extension components.

    >>> from slc.autotranslate.utils import split_filename
    >>> split_filename('foo_en.pdf')
    ('en', 'foo', 'pdf')

    >>> split_filename('en_bar.pdf')
    ('en', 'bar', 'pdf')

    >>> split_filename('enn_bar.txt')
    ('', 'enn_bar', 'txt')

    >>> split_filename('xx_bar.odt')
    ('', 'xx_bar', 'odt')

    """
    file_ext = ''
    if '.' in filename:
        filename, file_ext = filename.split('.')

    nl = filename.rsplit('.')
    l = nl[0].split('_')
    lang = '' 
    if len(l[0]) == 2:
        lang = l[0]
        base_filename = '_'.join(l[1:])
    elif len(l[-1]) == 2:
        lang = l[-1]
        base_filename = '_'.join(l[:-1])

    site = getSite()
    langtool = getToolByName(site, 'portal_languages')
    languages = [l[0] for l in langtool.listAvailableLanguages()]
        
    if lang == '' or lang not in languages:
        log.warn("File language could not be identified. Filename need to be "   
                 "prepended or appended with a valid language identifier, i.e "   
                 "en_factsheet.pdf' or 'factsheet_en.pdf'")
        return '', filename, file_ext

    return lang, base_filename, file_ext


def get_translations(folder, file_obj, base_filename, file_ext):
    """ 
    Return any files in folder that are deemed translations, for conforming
    to the file naming convention.

    For example: 'de_file.txt', 'fr_file.txt' and 'file_es.txt' are 
    translations of base_filename 'file.txt'.

    >>> folder.invokeFactory('Folder', 'parent')
    'parent'
    >>> parent = getattr(folder, 'parent')
    >>> de_parent = parent.addTranslation('de')

    >>> parent.invokeFactory('File', 'en_file.txt')
    'en_file.txt'
    >>> de_parent.invokeFactory('File', 'de_file.txt')
    'de_file.txt'
    >>> parent.invokeFactory('File', 'file_fr.txt')
    'file_fr.txt'
    >>> parent.invokeFactory('File', 'xx_file.txt')
    'xx_file.txt'
    >>> parent.invokeFactory('File', 'xxx.txt')
    'xxx.txt'
    >>> parent.objectIds()
    ['en_file.txt', 'file_fr.txt', 'xx_file.txt', 'xxx.txt']

    >>> from slc.autotranslate.utils import get_translations

    >>> en_file = getattr(parent, 'en_file.txt')

    >>> from pprint import pprint
    >>> pprint(get_translations(parent, en_file, 'file', 'txt'))
     {'de': <ATFile at /plone/Members/test_user_1_/parent-de/de_file.txt>,
     u'fr': <ATFile at /plone/Members/test_user_1_/parent/file_fr.txt>}

    """
    translations = {}
    file_ext = file_ext and '.%s' % file_ext or ''

    # Get all the translated parent folders, and see if there are 
    # translations conforming to base_filename in them
    translated_folders = folder.getTranslations()
    for langcode in translated_folders.keys():
        if langcode == folder.getLanguage():
            continue
        parent = translated_folders[langcode][0]
        prefixed = '%s_%s%s' % (langcode, base_filename, file_ext)
        suffixed = '%s_%s%s' % (base_filename, langcode, file_ext)
        for attr in (prefixed, suffixed):
            if hasattr(parent, attr):
                obj = getattr(parent, attr)
                translations[langcode] = obj

    langtool = getToolByName(folder, 'portal_languages')
    languages = langtool.listAvailableLanguages()
    for langcode, language in languages:
        prefixed = '%s_%s%s' % (langcode, base_filename, file_ext)
        suffixed = '%s_%s%s' % (base_filename, langcode, file_ext)
        for attr in (prefixed, suffixed):
            if hasattr(folder, attr):
                obj = getattr(folder, attr)
                if obj.UID() == file_obj.UID():
                    continue
                translations[langcode] = obj

    return translations


def translate_file(file):
    """ Set the file's language field and make sure that the file is moved
        to the parent folder with the same language 
    """
    parent = file.aq_parent 
    if not hasattr(parent, 'Schema'):
        return

    translate = parent.Schema().get('autoTranslateUploadedFiles').get(parent)
    if not translate:
        return 

    filename = file.getFile().filename
    lang, base_filename, file_ext = split_filename(filename)
    if not lang:
        # Warning message have already been logged.
        return

    translations = get_translations(parent, file, base_filename, file_ext)
    drop_duplicates = parent.Schema().get('ignoreDuplicateUploadedFiles').get(parent)
    if lang in translations.keys():
        if drop_duplicates:
            parent.manage_delObjects(file.id)
        else:
            obj = translations[lang]
            obj.setFile(file.getFile())
            parent.manage_delObjects(file.id)

        del translations[lang] 
        return
            
    try:
        file.setLanguage(lang)
    except AlreadyTranslated:
        log.warn("File with name %s could not be set to language '%s,"
                "a translation in this this language already exists!" \
                % (base_filename, lang))
    except CopyError:
        # Sometimes (i.e PloneFlashUploaded) files are not moveable, so we 
        # force this square peg into a round hole...
        if ITranslatable.providedBy(parent):
            new_parent = parent.getTranslation(lang)
            if new_parent:
                # Move to file to it's proper parent
                info = parent.manage_copyObjects([file.getId()])
                new_parent.manage_pasteObjects(info)
                parent.manage_delObjects(file.getId())
                file = new_parent._getOb(file.getId())

        file.getField('language').set(file, lang)

    keys = translations.keys()
    canonical = keys and translations[keys[0]].getCanonical() or None
    if canonical:
        file.addReference(canonical, RELATIONSHIP)
        
    can_lang = parent.getCanonicalLanguage()
    if lang == can_lang:
        file.setCanonical()

    file.reindexObject()
    file.invalidateTranslationCache()        

    if getConfiguration().debug_mode:
        if canonical:
            log.info('Canonical is %s' % str(canonical.absolute_url()))
        log.info('Translated uploaded file into %s' % lang)

    event.notify(AutoTranslatedFileEvent(file))


