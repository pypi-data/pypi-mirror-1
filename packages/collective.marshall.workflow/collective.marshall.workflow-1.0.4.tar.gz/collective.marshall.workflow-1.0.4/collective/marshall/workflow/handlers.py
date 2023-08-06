from Products.CMFCore.utils import getToolByName
from DateTime import DateTime
from zope.component import queryUtility
from interfaces import IStateTranslationUtility
import logging

def default_state_translation(source_state, target_workflow_id):
    return source_state

def setWorkflowState(obj, event):
    """
    """
    info = logging.getLogger("setWorkflowState").info
    
    wtool = getToolByName(obj, 'portal_workflow')
    review_state = wtool.getInfoFor(event.object, "review_state") 
    # try to get a translation table
    
    info('Workflow used %s' % event.data["workflow_id"])
    
    state_translation_utility = queryUtility(IStateTranslationUtility, name=event.data["workflow_id"])
    if not state_translation_utility:
        info('using default_state_translation')
        state_translation_utility = default_state_translation
    
    
    
    wtool = getToolByName(obj, 'portal_workflow')
    chain = wtool.getChainFor(obj)

    info(chain)

    for workflow_id in chain:
        workflow = wtool.getWorkflowById(workflow_id)
        if workflow:
            target_state = state_translation_utility(event.data["review_state"], workflow_id)
            info(target_state)
            if not target_state:
                target_state = workflow.initial_state
            target = {
                 'action'       : None,
                 'actor'        : 'gsxml',
                 'comments'     : 'imported',
                 'review_state' : target_state,
                 'time'         : DateTime(),
               }

            wtool.setStatusOf(workflow_id, obj, target)
            workflow.updateRoleMappingsFor(obj)


#wtool.doActionFor(obj, 'protect')
