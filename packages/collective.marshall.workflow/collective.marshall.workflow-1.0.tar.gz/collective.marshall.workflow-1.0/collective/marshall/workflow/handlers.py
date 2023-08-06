import logging
log = logging.getLogger("derserializedReviewState")

def logDeserializedReviewState(object, event):
    """
    """
    log.info("Received a IObjectReviewStateDeserializedEvent for %s. State: %s" % (event.object, event.data))
    