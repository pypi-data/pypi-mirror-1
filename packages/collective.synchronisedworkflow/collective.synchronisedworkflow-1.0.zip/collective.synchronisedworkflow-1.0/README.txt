Synchronised Workflow
=====================

collective.synchronisedworkflow allows items of content that are translations
to share the same workflow state as the canonical item. Any transition
performed on one of the content items will be replicated to all of its
siblings.

In addition, new content created as a translation will gain the same workflow
state as its siblings.

N.B.: This is currently Plone 4 only as it relies on some CMF changes. Plone 3
support is upcoming.