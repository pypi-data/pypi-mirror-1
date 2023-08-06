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
           <element name="workflow:review_state">
             <text />
           </element>
          </zeroOrMore>
  </define>
'''

class StateAttribute(SchemaAttribute):

    def get(self, instance):
        return instance.getPortalTypeName()

    def deserialize(self, instance, ns_data):
        value = ns_data.get(self.name)
        event.notify(ObjectReviewStateDeserializedEvent(instance, value))
        #instance._setPortalTypeName( value )

    def serialize(self, dom, parent_node, instance):
        wf_tool = getToolByName(instance, 'portal_workflow')
        value = wf_tool.getInfoFor(instance, "review_state")
        elname = "%s:%s"%(self.namespace.prefix, self.name)
        node = dom.createElementNS( Workflow.xmlns, elname )
        value_node = dom.createTextNode( str( value ) )
        node.appendChild( value_node )
        node.normalize()
        parent_node.appendChild( node )

class Workflow(XmlNamespace):
    
    xmlns = 'http://www.brainson.de/namespaces/workflow/'
    prefix = 'workflow'
    attributes = (
        StateAttribute('review_state'),
        )

    def getSchemaInfo( self ):
        return [
            ( "StateInfo", "optional", StateRNGSchemaFragment ),
              ]
      
