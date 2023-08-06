## Script (Python) "aviso_segunda_via"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=path='/pycon/2009/sobre-o-evento/inscricoes/'
##title=
##
response = context.REQUEST.response
response.setHeader('Content-Type', 'text/plain; charset=utf-8')

pendentes = context.portal_catalog(path=path, portal_type='Inscricao',
                                   getPaga=False, sort_on='sortable_title')

for inscricao in pendentes:
    if inscricao.getTipo > '3':
        continue
    dados = {
        'nome': inscricao.getNome,
        'email': inscricao.getEmail,
        'URL': inscricao.getURL(),
    }
    try:
        context.segunda_via(dados=dados)
        response.write('OK: %s\n' % dados['getNome'])
    except:
        response.write('ERRO: %s %s\n' % (dados['URL'], dados['getNome']))

