Introduction
============

This product adds a boolean 'autoTranslateFlashUploadedFiles' on all BaseFolder based
folders, which enables files uploaded with PloneFlashUpload to be automatically
translated. 

The language the file will be translated into, is determined form the file's
name. The file name must be prefixed or suffixed with a language code, followed
(or preceded) with an underscore.

The following are valid file names:
    
    de_factsheet.pdf
    factsheet_de.pdf


How To Use (Doc Tests):
=======================

Lets begin by creating a folder, in which we will upload our files.

    >>> folder = self.folder

First, we must set the 'autoTranslateFlashUploadedFiles' field on the parent folder

    >>> folder.Schema().get('autoTranslateFlashUploadedFiles', True).set(folder, True)

Next, we create a file and call the FlashUploadEvent.

    >>> fid = folder.invokeFactory('File', 'file.txt')
    >>> file = getattr(folder, fid)
    >>> f = open('src/slc.autotranslate/slc/autotranslate/de_file.txt')
    >>> file.setFile(f)

    >>> from z3c.widget.flashupload.interfaces import FlashUploadedEvent
    >>> from zope import event
    >>> event.notify(FlashUploadedEvent(file))

Check that translated file exists

    >>> hasattr(folder, 'file.txt-de')
    True
    
Check that the original has been deleted 

    >>> hasattr(folder, 'file.txt')
    False


    
