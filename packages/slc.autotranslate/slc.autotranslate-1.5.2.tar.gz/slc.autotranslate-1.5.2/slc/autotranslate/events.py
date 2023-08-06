import logging

from utils import translate_file 

log = logging.getLogger('slc.autotranslate/events.py')

def translate_flash_uploaded_file(evt):
    """ Event handler registered for FlashUploadEvent
    """
    file = evt.object
    translate_file(file)

def translate_added_file(file, evt):
    """ Event handler registered for normal file adding
    """
    translate_file(file)

