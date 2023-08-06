from zope import interface
try:
    from zope.component.interfaces import ObjectEvent, IObjectEvent
except ImportError:
    # Legacy Zope 3.2 support
    from zope.app.event.objectevent import ObjectEvent
    from zope.app.event.interfaces import IObjectEvent

class IAutoTranslatedFlashUploadEvent(IObjectEvent):
    """ Event gets fired when a flash uploaded item was translated via
        slc.autotranslate 
    """
    
class AutoTranslatedFlashUploadEvent(ObjectEvent):
    interface.implements(IAutoTranslatedFlashUploadEvent)
    
 
