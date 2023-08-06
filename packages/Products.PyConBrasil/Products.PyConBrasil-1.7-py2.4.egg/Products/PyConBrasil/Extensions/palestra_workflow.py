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
from Products.CMFCore.WorkflowTool import addWorkflowFactory
from Products.DCWorkflow.DCWorkflow import DCWorkflowDefinition
from Products.ExternalMethod.ExternalMethod import ExternalMethod
from Products.PyConBrasil.config import *

##code-section create-workflow-module-header #fill in your manual code here
##/code-section create-workflow-module-header


productname = 'PyConBrasil'

def setuppalestra_workflow(self, workflow):
    """Define the palestra_workflow workflow.
    """

    workflow.setProperties(title='palestra_workflow')

    ##code-section create-workflow-setup-method-header #fill in your manual code here
    ##/code-section create-workflow-setup-method-header


    for s in ['novo', 'pendente', 'aprovado', 'cancelado', 'reprovado']:
        workflow.states.addState(s)

    for t in ['re-submeter', 'salvar', 'aprovar', 'cancelar', 'reprovar']:
        workflow.transitions.addTransition(t)

    for v in ['review_history', 'comments', 'time', 'actor', 'action']:
        workflow.variables.addVariable(v)

    workflow.addManagedPermission('Modify portal content')
    workflow.addManagedPermission('Delete objects')
    workflow.addManagedPermission('View')
    workflow.addManagedPermission('Access contents information')

    for l in []:
        if not l in workflow.worklists.objectValues():
            workflow.worklists.addWorklist(l)

    ## Initial State

    workflow.states.setInitialState('novo')

    ## States initialization

    stateDef = workflow.states['novo']
    stateDef.setProperties(title="""Sendo criado""",
                           description="""""",
                           transitions=['salvar'])
    stateDef.setPermission('Modify portal content',
                           0,
                           ['Anonymous', 'Owner', 'Manager'])
    stateDef.setPermission('Delete objects',
                           0,
                           ['Anonymous', 'Owner', 'Manager'])

    stateDef = workflow.states['pendente']
    stateDef.setProperties(title="""Aguardando avaliação""",
                           description="""""",
                           transitions=['aprovar', 'reprovar'])
    stateDef.setPermission('Modify portal content',
                           0,
                           ['Manager'])
    stateDef.setPermission('Delete objects',
                           0,
                           ['Manager'])
    stateDef.setPermission('View',
                           0,
                           ['Owner', 'Anonymous', 'Manager', 'Reviewer'])
    stateDef.setPermission('Access contents information',
                           0,
                           ['Owner', 'Anonymous', 'Manager', 'Reviewer'])

    stateDef = workflow.states['aprovado']
    stateDef.setProperties(title="""Trabalho aprovado""",
                           description="""""",
                           transitions=['cancelar'])
    stateDef.setPermission('Modify portal content',
                           0,
                           ['Manager'])
    stateDef.setPermission('Delete objects',
                           0,
                           ['Manager'])
    stateDef.setPermission('View',
                           0,
                           ['Anonymous', 'Member', 'Manager'])
    stateDef.setPermission('Access contents information',
                           0,
                           ['Anonymous', 'Member', 'Manager'])

    stateDef = workflow.states['cancelado']
    stateDef.setProperties(title="""Apresentação cancelada""",
                           description="""""",
                           transitions=[])
    stateDef.setPermission('Modify portal content',
                           0,
                           [])
    stateDef.setPermission('Delete objects',
                           0,
                           [])
    stateDef.setPermission('View',
                           0,
                           ['Manager'])
    stateDef.setPermission('Access contents information',
                           0,
                           ['Manager'])

    stateDef = workflow.states['reprovado']
    stateDef.setProperties(title="""Trabalho reprovado""",
                           description="""""",
                           transitions=['re-submeter'])
    stateDef.setPermission('Modify portal content',
                           0,
                           ['Manager'])
    stateDef.setPermission('Delete objects',
                           0,
                           ['Manager'])
    stateDef.setPermission('View',
                           0,
                           ['Manager'])
    stateDef.setPermission('Access contents information',
                           0,
                           ['Manager'])

    ## Transitions initialization

    ## Creation of workflow scripts
    for wf_scriptname in ['antesResubmeter', 'depoisResubmeter']:
        if not wf_scriptname in workflow.scripts.objectIds():
            workflow.scripts._setObject(wf_scriptname,
                ExternalMethod(wf_scriptname, wf_scriptname,
                productname + '.palestra_workflow_scripts',
                wf_scriptname))

    transitionDef = workflow.transitions['re-submeter']
    transitionDef.setProperties(title="""Submeter novamente para avaliação""",
                                new_state_id="""pendente""",
                                trigger_type=1,
                                script_name="""antesResubmeter""",
                                after_script_name="""depoisResubmeter""",
                                actbox_name="""Submeter novamente para avaliação""",
                                actbox_url="""""",
                                actbox_category="""workflow""",
                                props={'guard_roles': 'Manager;Reviewer'},
                                )

    ## Creation of workflow scripts
    for wf_scriptname in ['antesSalvar', 'depoisSalvar']:
        if not wf_scriptname in workflow.scripts.objectIds():
            workflow.scripts._setObject(wf_scriptname,
                ExternalMethod(wf_scriptname, wf_scriptname,
                productname + '.palestra_workflow_scripts',
                wf_scriptname))

    transitionDef = workflow.transitions['salvar']
    transitionDef.setProperties(title="""Salvar inscrição""",
                                new_state_id="""pendente""",
                                trigger_type=1,
                                script_name="""antesSalvar""",
                                after_script_name="""depoisSalvar""",
                                actbox_name="""Salvar inscrição""",
                                actbox_url="""""",
                                actbox_category="""workflow""",
                                props={},
                                )

    ## Creation of workflow scripts
    for wf_scriptname in ['antesAprovar', 'depoisAprovar']:
        if not wf_scriptname in workflow.scripts.objectIds():
            workflow.scripts._setObject(wf_scriptname,
                ExternalMethod(wf_scriptname, wf_scriptname,
                productname + '.palestra_workflow_scripts',
                wf_scriptname))

    transitionDef = workflow.transitions['aprovar']
    transitionDef.setProperties(title="""Aprovar o trabalho""",
                                new_state_id="""aprovado""",
                                trigger_type=1,
                                script_name="""antesAprovar""",
                                after_script_name="""depoisAprovar""",
                                actbox_name="""Aprovar o trabalho""",
                                actbox_url="""""",
                                actbox_category="""workflow""",
                                props={'guard_roles': 'Manager;Reviewer'},
                                )

    transitionDef = workflow.transitions['cancelar']
    transitionDef.setProperties(title="""Cancelar este trabalho""",
                                new_state_id="""cancelado""",
                                trigger_type=1,
                                script_name="""""",
                                after_script_name="""""",
                                actbox_name="""Cancelar este trabalho""",
                                actbox_url="""""",
                                actbox_category="""workflow""",
                                props={'guard_roles': 'Manager'},
                                )

    ## Creation of workflow scripts
    for wf_scriptname in ['antesReprovar', 'depoisReprovar']:
        if not wf_scriptname in workflow.scripts.objectIds():
            workflow.scripts._setObject(wf_scriptname,
                ExternalMethod(wf_scriptname, wf_scriptname,
                productname + '.palestra_workflow_scripts',
                wf_scriptname))

    transitionDef = workflow.transitions['reprovar']
    transitionDef.setProperties(title="""Reprovar o trabalho""",
                                new_state_id="""reprovado""",
                                trigger_type=1,
                                script_name="""antesReprovar""",
                                after_script_name="""depoisReprovar""",
                                actbox_name="""Reprovar o trabalho""",
                                actbox_url="""""",
                                actbox_category="""workflow""",
                                props={'guard_roles': 'Manager; Reviewer'},
                                )

    ## State Variable
    workflow.variables.setStateVar('review_state')

    ## Variables initialization
    variableDef = workflow.variables['review_history']
    variableDef.setProperties(description="""Provides access to workflow history""",
                              default_value="""""",
                              default_expr="""state_change/getHistory""",
                              for_catalog=0,
                              for_status=0,
                              update_always=0,
                              props={'guard_permissions': 'Request review; Review portal content'})

    variableDef = workflow.variables['comments']
    variableDef.setProperties(description="""Comments about the last transition""",
                              default_value="""""",
                              default_expr="""python:state_change.kwargs.get('comment', '')""",
                              for_catalog=0,
                              for_status=1,
                              update_always=1,
                              props=None)

    variableDef = workflow.variables['time']
    variableDef.setProperties(description="""Time of the last transition""",
                              default_value="""""",
                              default_expr="""state_change/getDateTime""",
                              for_catalog=0,
                              for_status=1,
                              update_always=1,
                              props=None)

    variableDef = workflow.variables['actor']
    variableDef.setProperties(description="""The ID of the user who performed the last transition""",
                              default_value="""""",
                              default_expr="""user/getId""",
                              for_catalog=0,
                              for_status=1,
                              update_always=1,
                              props=None)

    variableDef = workflow.variables['action']
    variableDef.setProperties(description="""The last transition""",
                              default_value="""""",
                              default_expr="""transition/getId|nothing""",
                              for_catalog=0,
                              for_status=1,
                              update_always=1,
                              props=None)

    ## Worklists Initialization


    # WARNING: below protected section is deprecated.
    # Add a tagged value 'worklist' with the worklist name to your state(s) instead.

    ##code-section create-workflow-setup-method-footer #fill in your manual code here
    ##/code-section create-workflow-setup-method-footer



def createpalestra_workflow(self, id):
    """Create the workflow for PyConBrasil.
    """

    ob = DCWorkflowDefinition(id)
    setuppalestra_workflow(self, ob)
    return ob

addWorkflowFactory(createpalestra_workflow,
                   id='palestra_workflow',
                   title='palestra_workflow')

##code-section create-workflow-module-footer #fill in your manual code here
##/code-section create-workflow-module-footer

