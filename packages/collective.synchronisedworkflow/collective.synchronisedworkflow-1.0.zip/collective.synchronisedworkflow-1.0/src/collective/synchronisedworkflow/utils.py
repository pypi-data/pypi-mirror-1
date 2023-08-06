def forceWorkflowState(context, action):
    context = action.target
    if context.isCanonical():
        return
    wft = context.portal_workflow
    canonical = context.getCanonical()
    workflows = wft.getWorkflowsFor(context)
    for workflow in workflows:
        wf_id = workflow.id
        status = wft.getStatusOf(wf_id, canonical)
        wft.setStatusOf(wf_id, context, status)


def successEvent(context, action):
    if hasattr(context, '_v_no_recursion_thanks'):
        # If we don't do this we get into a recursive mess because propagate
        # will cause the same type of events to be thrown
        return
    propagateAction(context.portal_workflow, context, action.action)

def propagateAction(wft, ob, action):
    for t, state in ob.getTranslations().values():
        if t == ob:
            # This one has been transitioned already, by definition
            continue
        t._v_no_recursion_thanks = True
        wft.doActionFor(t, action)
        del t._v_no_recursion_thanks