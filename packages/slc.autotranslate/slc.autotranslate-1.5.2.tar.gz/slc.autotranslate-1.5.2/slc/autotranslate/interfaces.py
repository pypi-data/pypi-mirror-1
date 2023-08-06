from zope import interface
try:
    from zope.component.interfaces import ObjectEvent, IObjectEvent
except ImportError:
    # Legacy Zope 3.2 support
    from zope.app.event.objectevent import ObjectEvent
    from zope.app.event.interfaces import IObjectEvent

class IAutoTranslatedFileEvent(IObjectEvent):
    """ Event gets fired when an uploaded file was translated via
        slc.autotranslate 
    """
    
class AutoTranslatedFileEvent(ObjectEvent):
    interface.implements(IAutoTranslatedFileEvent)
    
 
