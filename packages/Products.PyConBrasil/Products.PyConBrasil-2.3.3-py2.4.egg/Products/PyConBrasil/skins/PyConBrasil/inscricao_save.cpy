## Controller Python Script "inscricao_save"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Muda de estado o objeto Inscricao quando salvo pela primeira vez
##

from Products.CMFCore.utils import getToolByName

portal_workflow = getToolByName(context, 'portal_workflow')
portal_membership = getToolByName(context, 'portal_membership')

review_state = portal_workflow.getInfoFor(context, 'review_state')

message = ''

if review_state == 'novo':
    if portal_membership.isAnonymousUser():
        context.setCreators(('(anonymous)',))
    if context.emPreInscricao():
        portal_workflow.doActionFor(context, 'salvar')
        message = (u'Sua pré-inscrição foi recebida. Você receberá um '
                   u'e-mail solicitando a confirmação quando o período '
                   u'das inscrições for aberto.')
    else:
        portal_workflow.doActionFor(context, 'registrar')
        message = (u'Cadastro realizado, agora proceda com o '
                   u'pagamento da taxa de inscricao. Aguardamos sua '
                   u'presenca no evento.')
elif review_state == 'em_confirmacao':
    if state.button == 'cancelar_confirmacao':
        portal_workflow.doActionFor(context, 'cancelar_confirmacao')
        message = (u'A confirmação da sua pré-inscrição foi cancelada. '
                   u'Você ainda precisa confirmá-la caso deseje participar '
                   u'do evento.')
    else:
        portal_workflow.doActionFor(context, 'finalizar_confirmacao')
        message = (u'Sua pré-inscrição foi confirmada. Aguardamos sua '
                   u'presença no evento.')

if message:
    context.plone_utils.addPortalMessage(message)
return state.set(context=context)
