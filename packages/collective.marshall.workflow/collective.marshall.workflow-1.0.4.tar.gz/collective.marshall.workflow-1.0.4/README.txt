Introduction
============

This product adds the export and import of the object's workflow state to the atxml
marshaller. If you have the same workflow states on the export side and on the import
side, it should just work out of the box.

A default handler is already included. It looks up a named utility "IStateTranslationUtility", with
the name of the remote workflow. A parameter is the name of the local workflow.
It should be able to translate from the remote states to local states. If no such utility is found,
it is expected, that the state-names on the remote side match those on the local side.

An example for this utility could be this::

    <utility
        provides="collective.marshall.workflow.interfaces.IStateTranslationUtility"
        component=".utilities.simple_publication_workflow_state_translator"
        name="simple_publication_workflow"
        />

    def simple_publication_workflow_state_translator(state, target_workflow_id):
        translation = {}
        if target_workflow_id == "simple_protection_and_publication_workflow":
            translation = {'private': 'private',
                           'published': 'protected'}

        return translation.get(state, None)

If the utility returns None, it is expected, that the remote name matches the local name.

The default handler does not call transitions, but instead sets the state directly.
Instead of using the default handler, you can define your own handler::

  <subscriber
       for="*
           collective.marshall.workflow.interfaces.IObjectReviewStateDeserializedEvent"
      handler=".handlers.yourHandler"
      />

  def logDeserializedReviewState(object, event):
      print "Received a IObjectReviewStateDeserializedEvent for %s. State: %s" % (event.object, event.data)

So the handler receives the object and the data, which is the state as string, e.g. "published".

A very good default handler is already included.

Authors
=======

- Oliver Roch <oliver.roch@brainson.de>
- Daniel Kraft <daniel.kraft@d9t.de>

