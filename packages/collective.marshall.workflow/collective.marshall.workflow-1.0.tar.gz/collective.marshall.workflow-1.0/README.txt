Introduction
============

This products adds the export of the object's workflow state to the atxml
marshaller. As it could be difficult to set the state on the target site,
because there might be workflow transition-scripts which should NOT be
executed, the import only fires an event. You can subscribe to it:

<subscriber
    for="*
         collective.marshall.workflow.interfaces.IObjectReviewStateDeserializedEvent"
    handler=".handlers.yourHandler"
    /> 

Example for handler:
--------------------

def logDeserializedReviewState(object, event):
    print "Received a IObjectReviewStateDeserializedEvent for %s. State: %s" % (event.object, event.data)

So the handler receives the object and the data, which is the state as string, e.g. "published".

