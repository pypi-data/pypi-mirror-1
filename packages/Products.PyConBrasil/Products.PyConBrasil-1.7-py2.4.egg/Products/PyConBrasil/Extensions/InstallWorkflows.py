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


from Products.CMFCore.utils import getToolByName
from Products.ExternalMethod.ExternalMethod import ExternalMethod

##code-section module-header #fill in your manual code here
##/code-section module-header

def installWorkflows(self, package, out):
    """Install the custom workflows for this product."""

    productname = 'PyConBrasil'
    workflowTool = getToolByName(self, 'portal_workflow')

    ourProductWorkflow = ExternalMethod('temp', 'temp',
                                        productname+'.'+'inscricoes_workflow',
                                        'createinscricoes_workflow')
    workflow = ourProductWorkflow(self, 'inscricoes_workflow')
    if 'inscricoes_workflow' in workflowTool.listWorkflows():
        print >> out, 'inscricoes_workflow already in workflows.'
    else:
        workflowTool._setObject('inscricoes_workflow', workflow)
    workflowTool.setChainForPortalTypes(['Inscricoes'], workflow.getId())

    ourProductWorkflow = ExternalMethod('temp', 'temp',
                                        productname+'.'+'inscricao_workflow',
                                        'createinscricao_workflow')
    workflow = ourProductWorkflow(self, 'inscricao_workflow')
    if 'inscricao_workflow' in workflowTool.listWorkflows():
        print >> out, 'inscricao_workflow already in workflows.'
    else:
        workflowTool._setObject('inscricao_workflow', workflow)
    workflowTool.setChainForPortalTypes(['Inscricao', 'Imprensa'], workflow.getId())

    ourProductWorkflow = ExternalMethod('temp', 'temp',
                                        productname+'.'+'palestra_workflow',
                                        'createpalestra_workflow')
    workflow = ourProductWorkflow(self, 'palestra_workflow')
    if 'palestra_workflow' in workflowTool.listWorkflows():
        print >> out, 'palestra_workflow already in workflows.'
    else:
        workflowTool._setObject('palestra_workflow', workflow)
    workflowTool.setChainForPortalTypes(['Palestra', 'Treinamento', 'PalestraRelampago'], workflow.getId())

    ##code-section after-workflow-install #fill in your manual code here
    ##/code-section after-workflow-install

    return workflowTool

def uninstallWorkflows(self, package, out):
    """Deinstall the workflows.

    This code doesn't really do anything, but you can place custom
    code here in the protected section.
    """

    ##code-section workflow-uninstall #fill in your manual code here
    ##/code-section workflow-uninstall

    pass
