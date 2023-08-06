Introduction
============

This product provides an alternative type of workflow definition. It works
much like a regular workflow, but instead of granting permissions when 
entering a particular state, it takes them away from the selected roles.

The original use case was to support "confidential" content items via a
secondary workflow. The primary chain on the type has a publishing workflow
that will grant the View permission to various roles in various states. The
secondary 'confidentiality workflow' has two states: 'normal' and
'confidential'. In the 'normal' state, no roles are selected for the View
permission, and so the role mappings from the primary workflow apply. However,
in the 'confidential' state, Anonymous, Authenticated and Member have been
selected for the View permission and so these roles no longer have the ability
to view the item.

Note that the 'acquire' flag should almost always be off. The subtractive
workflow will set the acquire property in the same way as the default
workflow definition, but the results will probably not be what you expect,
since permissions that were "turned off" may well be acquired.

Also note that group-to-local role mappings are not "subtractive" and work
exactly as in the standard workflow definition. In general, local roles are
always inherited in Zope (although Plone has an extension to turn this off).

The effects of multiple workflows
----------------------------------

This product depends on an interpretation of the DCWorkflow permissions system
as follows:

  * If there are multiple workflows in a chain, the item's state is determined
  by all the workflows, not just the last one.
  * In particular, the permission settings in all workflows in the chain apply
  at all times. Later workflows can override earlier ones.
  
To support this, an event handler is installed that will, when a transition
occurs, "re-play" the updateRoleMappings() call for all workflows in the chain
(there is an optimisation to avoid duplicate work if there's only one
workflow in the chain). It will do nothing if there are no subtractive
workflows in the chain, but as soon as there is one, you will get this
behaviour.

Thus, if you have a subtractive workflow as the second workflow in a
two-workflow chain, and you invoke a transition from either the first or the
second workflow, the permissions from both will apply, with the subtractive
workflow allowed to override the normal workflow.

Note that this may affect existing multi-workflow chains, because by default,
DCWorkflow does not "re-play" the role mappings in this way, letting instead
the most recently entered state determine the role mappings and fully
overriding roles from the current state of any other workflows in the chain.
