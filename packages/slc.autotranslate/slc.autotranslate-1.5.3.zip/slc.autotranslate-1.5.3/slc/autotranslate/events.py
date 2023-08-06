import logging

from utils import translate_file 

log = logging.getLogger('slc.autotranslate/events.py')

def translate_flash_uploaded_file(evt):
    """ Event handler registered for FlashUploadEvent
    """
    file = evt.object
    if getattr(file, '_autotranslate_already_handled', False):
        return
    translate_file(file)
    file._autotranslate_already_handled = True

def translate_added_file(file, evt):
    """ Event handler registered for normal file adding
    """
    if getattr(file, '_autotranslate_already_handled', False):
        return
    translate_file(file)
    file._autotranslate_already_handled = True

