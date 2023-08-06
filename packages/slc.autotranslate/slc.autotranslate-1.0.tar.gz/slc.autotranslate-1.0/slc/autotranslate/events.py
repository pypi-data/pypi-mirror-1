import logging
from zope import event
from interfaces import AutoTranslatedFlashUploadEvent

log = logging.getLogger('slc.autotranslate/events.py')

def translate_uploaded_files(evt):
    """ Event handler registered for FlashUploadEvent
    """
    parent = evt.object.aq_parent 
    translate = parent.Schema().get('autoTranslateFlashUploadedFiles').get(parent)
    if not translate:
        return 

    file = evt.object
    file_obj = file.getFile()
    file_name, file_ext = file_obj.filename.split('.')
    l = file_name.split('_')
    if len(l[0]) == 2:
        lang = l[0]
    elif len(l[-1]) == 2:
        lang = l[-1]
    else:
        log.warn("File language could not be identified. Filename need to be" + 
                 "prepended or appended with the language identifier, i.e" + 
                 "en_factsheet.pdf' or 'factsheet_en.pdf'")
        return

    trans_file = file.addTranslation(lang)
    if trans_file.getFile().filename is None:
        # Sometimes the new translation doesn't contain the actual file
        trans_file.setFile(file_obj)

    parent.manage_delObjects(ids=[file.getId()])
    event.notify(AutoTranslatedFlashUploadEvent(trans_file))
        

