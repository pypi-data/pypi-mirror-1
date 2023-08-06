from utils import propagateAction

def notifySuccess(self, ob, action, result=None):

    """ Notify all applicable workflows that an action has taken place.
    """
    wfs = self.getWorkflowsFor(ob)
    for wf in wfs:
        wf.notifySuccess(ob, action, result)
    propagateAction(self, ob, action)