from zope.lifecycleevent.interfaces import IObjectModifiedEvent
from zope.interface import Interface, Attribute


class IObjectReviewStateDeserializedEvent(IObjectModifiedEvent):
    """
    """
    
    data = Attribute("Resolved data from namespace.")
    
class IStateTranslationUtility(Interface):
    """
    """