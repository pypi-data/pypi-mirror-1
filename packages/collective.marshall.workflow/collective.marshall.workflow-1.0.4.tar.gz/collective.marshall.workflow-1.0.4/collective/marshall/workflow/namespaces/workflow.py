from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from Products.Marshall.handlers.atxml import XmlNamespace
from Products.Marshall.handlers.atxml import SchemaAttribute
from Products.Marshall import utils
from zope import event
from collective.marshall.workflow.events import ObjectReviewStateDeserializedEvent

StateRNGSchemaFragment = '''
  <define name="StateInfo"
          xmlns:cmf="http://www.brainson.de/namespaces/workflow"
          datatypeLibrary="http://www.w3.org/2001/XMLSchema-datatypes"
          xmlns="http://relaxng.org/ns/structure/1.0">
           <element name="workflow:status">
             <attribute name="id" /> 
             <text /> 
           </element>
          </zeroOrMore>
  </define>
'''

class StateAttribute(SchemaAttribute):

    def get(self, instance):
        return instance.getPortalTypeName()
    
    def processXmlValue(self, context, value):
        """ callback to process text nodes
        """
        value = value and value.strip()
        if not value:
            return
        data = context.getDataFor( self.namespace.xmlns )
        data[self.name] = {"review_state": value,
                           "workflow_id" : context.node.get("id"),
                          }
 

    def deserialize(self, instance, ns_data):
        data = ns_data.get(self.name)
        event.notify(ObjectReviewStateDeserializedEvent(instance, data))
        #instance._setPortalTypeName( value )

    def serialize(self, dom, parent_node, instance):
        wf_tool = getToolByName(instance, 'portal_workflow')
        value = wf_tool.getInfoFor(instance, "review_state")
        elname = "%s:%s"%(self.namespace.prefix, self.name)
        node = dom.createElementNS( Workflow.xmlns, elname )
        
        workflow_id = dom.createAttribute("id")
        #state = dom.createAttribute("state")
        
        workflow_id.value = ",".join(wf_tool.getChainFor(instance))
        #state.value = value
        
        node.setAttributeNode(workflow_id)
        #node.setAttributeNode(state)
        
        value_node = dom.createTextNode( str( value ) )
        node.appendChild( value_node )
        node.normalize()
        parent_node.appendChild( node )

class Workflow(XmlNamespace):
    
    xmlns = 'http://www.brainson.de/namespaces/workflow/'
    prefix = 'workflow'
    attributes = (
        StateAttribute('status'),
        )

    def getSchemaInfo( self ):
        return [
            ( "StateInfo", "optional", StateRNGSchemaFragment ),
              ]
      
