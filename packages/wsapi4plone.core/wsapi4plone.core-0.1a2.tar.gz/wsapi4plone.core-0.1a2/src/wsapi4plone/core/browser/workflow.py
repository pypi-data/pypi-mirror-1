from zope.app.component.hooks import getSite
from zope.interface import implements

from interfaces import IWorkflow
from wsapi import WSAPI

class Workflow(WSAPI):
    implements(IWorkflow)

    def get_workflow(self, path=''):
        """
        @param path - string to the path of the wanted object
        """
        obj = self.builder(self.context, path)
        portal_workflow = getSite().portal_workflow
        results = {}

        self.logger.info("- get_workflow - Getting workflow state for %s." % (obj))

        results['state'] = current_state = portal_workflow.getInfoFor(obj, 'review_state')
        obj_content_type = obj.getTypeInfo().getId()
        chains = portal_workflow.getChainForPortalType(obj_content_type)

        results['transitions'] = []
        for chain in chains:
            # get state definitions for the given chain: portal_workflow.chain.states._mapping.keys()
            states = portal_workflow.get(chains[-1], None).states
            # get the availble transitions that we can validate against the wanted transition
            state_definition = states.get(current_state, None)
            if state_definition:
                for transition in state_definition.getTransitions():
                    results['transitions'].append(transition)
        return results

    def set_workflow(self, transition, path=''):
        """
        @param transition - string representing the workflow transition action
        @param path - string to the path of the wanted object
        """
        obj = self.builder(self.context, path)
        portal_workflow = getSite().portal_workflow

        self.logger.info("- set_workflow - Transitioning (%s) workflow state for %s." % (transition, obj))

        # action/transition verification/validation is done in doActionFor
        portal_workflow.doActionFor(obj, transition)
        return