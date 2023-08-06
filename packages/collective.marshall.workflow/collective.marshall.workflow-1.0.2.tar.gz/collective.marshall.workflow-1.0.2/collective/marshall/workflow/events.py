from zope.interface import implements
from zope.lifecycleevent import ObjectModifiedEvent
from interfaces import IObjectReviewStateDeserializedEvent

class ObjectReviewStateDeserializedEvent(ObjectModifiedEvent):
    """
        The marshaller in namespaces.wfstate received a review_state.
        Let's transition the object into the desired state.
    """
    implements(IObjectReviewStateDeserializedEvent)
    
    def __init__(self, object, data):
        self.object = object
        self.data = data
 
