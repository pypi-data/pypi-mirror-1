## Controller Python Script "imprensa_save"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Muda de estado o objeto Imprensa quando salvo pela primeira vez
##

from Products.CMFCore.utils import getToolByName

portal_workflow = getToolByName(context, 'portal_workflow')
portal_membership = getToolByName(context, 'portal_membership')

if portal_workflow.getInfoFor(context, 'review_state') == 'novo':
    if portal_membership.isAnonymousUser():
        context.setCreators(('(anonymous)',))
    portal_workflow.doActionFor(context, 'registrar')

return state

