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


# Workflow Scripts for: inscricao_workflow

##code-section workflow-script-header #fill in your manual code here
##/code-section workflow-script-header


def marcaComoPaga(self, state_change, **kw):
    obj = state_change.object
    obj.setPaga(True)
    obj.reindexObject()



def enviaEmailConfirmacao(self, state_change, **kw):
    obj = state_change.object
    template = obj.template_inscricao(obj)
    params = {
        'getNome': obj.getNome(),
        'getEmail': obj.getEmail(),
        'URL': obj.absolute_url(),
    }
    obj.MailHost.send(template % params)


