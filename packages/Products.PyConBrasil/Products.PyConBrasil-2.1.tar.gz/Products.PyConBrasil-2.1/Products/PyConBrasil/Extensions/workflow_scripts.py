from Products.CMFPlone.utils import log, getToolByName

def marcaComoPaga(self, state_change, **kw):
    obj = state_change.object
    obj.setPaga(True)
    obj.reindexObject()
    template = obj.template_pagamento_realizado(obj)
    params = {
        'nome': obj.getNome(),
        'email': obj.getEmail(),
        'URL': obj.absolute_url(),
    }
    obj.MailHost.send(template % params)

def enviaEmailConfirmacao(self, state_change, **kw):
    obj = state_change.object
    template = obj.template_inscricao(obj)
    params = {
        'nome': obj.getNome(),
        'email': obj.getEmail(),
        'URL': obj.absolute_url(),
    }
    obj.MailHost.send(template % params)

def depoisSalvar(self, state_change, **kw):
    obj = state_change.object
    template = obj.template_recebimento_trabalho(obj)
    params = {
        'nome': obj.getNome(),
        'email': obj.getEmail(),
        'titulo': obj.Title(),
    }
    obj.MailHost.send(template % params)

def enviaEmailPreInscritos(self, state_change, **kw):
    obj = state_change.object
    template = obj.template_confirmacao(obj)
    inscricoes = obj.portal_catalog(portal_type='Inscricao',
                                    review_state='pre-inscrito')
    for inscricao in inscricoes:
        params = {
            'nome': inscricao.getNome,
            'email': inscricao.getEmail,
            'UID': inscricao.UID,
        }
        obj.MailHost.send(template % params)

