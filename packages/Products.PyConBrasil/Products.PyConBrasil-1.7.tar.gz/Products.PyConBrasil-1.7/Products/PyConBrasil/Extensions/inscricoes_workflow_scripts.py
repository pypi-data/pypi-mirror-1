# -*- coding: utf-8 -*-
#
# File: PyConBrasil.py
#
# Copyright (c) 2007 by Associação Python Brasil
# Generator: ArchGenXML Version 1.5.1-svn
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
#

__author__ = """Jean Rodrigo Ferri / Dorneles Treméa / Fabiano Weimar / Rodrigo Senra /
Érico Andrei <contato@pythobrasil.com.br>"""
__docformat__ = 'plaintext'


# Workflow Scripts for: inscricoes_workflow

##code-section workflow-script-header #fill in your manual code here
##/code-section workflow-script-header


def enviaEmailPreInscritos(self, state_change, **kw):
    """Envia um email para cada pré-inscrito solicitando a confirmação
    da inscrição.
    """
    from Products.CMFPlone.utils import getToolByName
    obj = state_change.object
    template = obj.template_confirmacao(obj)
    portal_catalog = getToolByName(obj, 'portal_catalog')
    inscricoes = portal_catalog(portal_type='Inscricao',
                                review_state='pre-inscrito')
    for inscricao in inscricoes:
        params = {
            'getNome': inscricao.getNome,
            'getEmail': inscricao.getEmail,
            'UID': inscricao.UID,
        }
        obj.MailHost.send(template % params)


