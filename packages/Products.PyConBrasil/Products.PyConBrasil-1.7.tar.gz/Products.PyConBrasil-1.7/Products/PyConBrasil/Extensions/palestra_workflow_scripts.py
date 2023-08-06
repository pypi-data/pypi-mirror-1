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


# Workflow Scripts for: palestra_workflow

##code-section workflow-script-header #fill in your manual code here
##/code-section workflow-script-header


def depoisSalvar(self, state_change, **kw):
    from Products.CMFPlone.utils import log, getToolByName
    object = state_change.object
    template = object.template_recebimento_trabalho(object)
    MailHost = getToolByName(object, 'MailHost')
    params = {
        'nome': object.getNome(),
        'email': object.getEmail(),
        'titulo': object.Title(),
    }
    log('Enviando e-mail sobre trabalho com id %s de %s' % (object.getId(),params['nome']))
    MailHost.send(template % params)
    log('E-mail enviado! (id %s de %s)' % (object.getId(),params['nome']))



def antesAprovar(self, state_change, **kw):
    pass



def depoisResubmeter(self, state_change, **kw):
    pass



def depoisReprovar(self, state_change, **kw):
    pass



def depoisAprovar(self, state_change, **kw):
    pass



def antesSalvar(self, state_change, **kw):
    pass



def antesReprovar(self, state_change, **kw):
    pass



def antesResubmeter(self, state_change, **kw):
    pass


