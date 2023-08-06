import logging
log = logging.getLogger('slc.autotranslate.events.py')

def translate_uploaded_files(event):
    """
    """
    parent = event.object.aq_parent 
    translate = parent.Schema().get('autoTranslateFlashUploadedFiles').get(parent)
    if not translate:
        return 

    file = event.object
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
    parent.manage_delObjects(ids=[file.getId()])
        



        
