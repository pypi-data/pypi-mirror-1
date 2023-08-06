Introduction
============

This product adds a boolean 'autoTranslateUploadedFiles' on all BaseFolder based
folders, which enables any uploaded files to be automatically translated. 

'Translation' here merely refers to a procedure whereby the file's language 
is identified and its language code set accordingly (via setLanguage).

The language that the file will be translated into, is determined form the file's
name. The file name must be prefixed or suffixed with a language code, followed
(or preceded) with an underscore.

The following are valid file names:
    
    - de_factsheet.pdf
    - factsheet_de.pdf

How To Use (Doc Tests):
=======================

First, we import everything we need:

    >>> from z3c.widget.flashupload.interfaces import FlashUploadedEvent
    >>> from Products.Archetypes.event import ObjectInitializedEvent
    >>> from zope import event

We will create the folder in which we upload our test files inside the test
user's Member folder.

    >>> self.folder.invokeFactory('Folder', 'publications')
    'publications'
    >>> folder = self.folder._getOb('publications')

To enable the autotranslation feature, we must set the 'autoTranslateUploadedFiles' 
field on the parent folder. 

This is a field added via schema-extension, so we cannot use an Archetypes
generated mutator.

    >>> folder.Schema().get('autoTranslateUploadedFiles', True).set(folder, True)

Now we simulate the uploading of 2 files via PloneFlashUpload.
Each time we create a file inside our folder, and then call the FlashUploadedEvent.

    >>> for fn in ['en_file.txt', 'de_file.txt']:
    ...     fid = folder.invokeFactory('File', fn)
    ...     file = getattr(folder, fid)
    ...     f = open('src/slc.autotranslate/slc/autotranslate/tests/%s' % fn)
    ...     file.setFile(f)
    ...     event.notify(FlashUploadedEvent(file))

Let's see if our uploaded files were set correctly to their indicated languages, 
and also that the canonical was set properly:

    >>> file = getattr(folder, 'en_file.txt')
    >>> file.getLanguage()
    'en'

    >>> file.getCanonical()
    <ATFile at /plone/Members/test_user_1_/publications/en_file.txt> 

    >>> file = getattr(folder, 'de_file.txt')
    
    >>> file.getLanguage()
    'de'

    >>> file.getCanonical()
    <ATFile at /plone/Members/test_user_1_/publications/en_file.txt> 

File names that end with the language code (as apposed to it being prefixed) 
are also valid. We'll test now that this is indeed the case.

First we again upload a file, this time file_es.txt (Spanish):
    
    >>> fid = folder.invokeFactory('File', 'file_es.txt')
    >>> file = getattr(folder, fid)
    >>> f = open('src/slc.autotranslate/slc/autotranslate/tests/file_es.txt')
    >>> file.setFile(f)

Now we fire the event. This time, we use Archetypes' ObjectInitializedEvent, to
show that normally added (as opposed to PloneFlashUpload) files are also translated.

    >>> event.notify(ObjectInitializedEvent(file))

Let's test that the file's language and the canonical was set correctly:

    >>> file = getattr(folder, 'file_es.txt')
    >>> file.getLanguage()
    'es'

    >>> file.getCanonical()
    <ATFile at /plone/Members/test_user_1_/publications/en_file.txt> 
    

Additional Tests:
=================

1. We test now that every file's language as well as it's relationship to the
canonical is properly set, when the canonical is uploaded last.

First, we clear the folder to start anew.

    >>> folder.manage_delObjects(folder.objectIds())
    >>> folder.objectIds()
    []

Create the files and call the event:
    
    >>> filenames = ['de_file.txt', 'file_es.txt', 'fr_file.txt', 'en_file.txt']
    >>> for fn in filenames:
    ...     fid = folder.invokeFactory('File', fn)
    ...     file = getattr(folder, fid)
    ...     f = open('src/slc.autotranslate/slc/autotranslate/tests/%s' % fn)
    ...     file.setFile(f)
    ...     event.notify(ObjectInitializedEvent(file))

Test that everything is still in order:

    >>> file = getattr(folder, 'de_file.txt')
    >>> file.getLanguage()
    'de'

    >>> file.getCanonical()
    <ATFile at /plone/Members/test_user_1_/publications/en_file.txt> 

    >>> file = getattr(folder, 'file_es.txt')
    >>> file.getLanguage()
    'es'

    >>> file.getCanonical()
    <ATFile at /plone/Members/test_user_1_/publications/en_file.txt> 

    >>> file = getattr(folder, 'fr_file.txt')
    >>> file.getLanguage()
    'fr'

    >>> file.getCanonical()
    <ATFile at /plone/Members/test_user_1_/publications/en_file.txt> 

    >>> file = getattr(folder, 'en_file.txt')
    >>> file.getLanguage()
    'en'

    >>> file.getCanonical()
    <ATFile at /plone/Members/test_user_1_/publications/en_file.txt> 

Tear down:
    >>> folder.manage_delObjects(filenames)


2. Test that translated files are also moved to the appropriate folders. In
other words, a file translated to another language, must now also reside in
that same language's version of the file's parent folder.
    
    >>> de_folder = folder.addTranslation('de')

    >>> filenames = ['de_file.txt', 'en_file.txt']
    >>> for fn in filenames:
    ...     fid = folder.invokeFactory('File', fn)
    ...     file = getattr(folder, fid)
    ...     f = open('src/slc.autotranslate/slc/autotranslate/tests/%s' % fn)
    ...     file.setFile(f)
    ...     event.notify(ObjectInitializedEvent(file))

    >>> folder.objectIds()
    ['en_file.txt']

    >>> de_folder.objectIds()
    ['de_file.txt']

Tear down:
    >>> folder.manage_delObjects('en_file.txt')
    >>> de_folder.manage_delObjects('de_file.txt')

3. Test that files whose names do not conform to the slc.autotranslate naming
convention are still uploaded normally

    >>> fid = folder.invokeFactory('File', 'file.txt')
    >>> file = getattr(folder, fid)
    >>> f = open('src/slc.autotranslate/slc/autotranslate/tests/file.txt')
    >>> file.setFile(f)
    >>> event.notify(ObjectInitializedEvent(file))

    >>> folder.objectIds()
    ['file.txt']


