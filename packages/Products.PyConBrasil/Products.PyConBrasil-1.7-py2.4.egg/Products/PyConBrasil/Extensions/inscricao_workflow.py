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

def setupinscricao_workflow(self, workflow):
    """Define the inscricao_workflow workflow.
    """

    workflow.setProperties(title='inscricao_workflow')

    ##code-section create-workflow-setup-method-header #fill in your manual code here
    ##/code-section create-workflow-setup-method-header


    for s in ['novo', 'registrado', 'pre-inscrito', 'em_confirmacao']:
        workflow.states.addState(s)

    for t in ['finalizar_confirmacao', 'pagar', 'registrar', 'iniciar_confirmacao', 'confirmar', 'salvar', 'cancelar_confirmacao']:
        workflow.transitions.addTransition(t)

    for v in ['review_history', 'comments', 'time', 'actor', 'action']:
        workflow.variables.addVariable(v)

    workflow.addManagedPermission('Modify portal content')
    workflow.addManagedPermission('Delete objects')

    for l in []:
        if not l in workflow.worklists.objectValues():
            workflow.worklists.addWorklist(l)

    ## Initial State

    workflow.states.setInitialState('novo')

    ## States initialization

    stateDef = workflow.states['novo']
    stateDef.setProperties(title="""Sendo criado""",
                           description="""""",
                           transitions=['registrar', 'salvar'])
    stateDef.setPermission('Modify portal content',
                           0,
                           ['Anonymous', 'Owner', 'Manager'])
    stateDef.setPermission('Delete objects',
                           0,
                           ['Anonymous', 'Owner', 'Manager'])

    stateDef = workflow.states['registrado']
    stateDef.setProperties(title="""Registrado""",
                           description="""""",
                           transitions=['pagar'])
    stateDef.setPermission('Delete objects',
                           0,
                           ['Manager'])
    stateDef.setPermission('Modify portal content',
                           0,
                           ['Manager'])

    stateDef = workflow.states['pre-inscrito']
    stateDef.setProperties(title="""Pré-inscrito""",
                           description="""""",
                           transitions=['confirmar', 'iniciar_confirmacao'])
    stateDef.setPermission('Delete objects',
                           0,
                           ['Manager'])
    stateDef.setPermission('Modify portal content',
                           0,
                           ['Owner', 'Manager'])

    stateDef = workflow.states['em_confirmacao']
    stateDef.setProperties(title="""Em Confirmação""",
                           description="""""",
                           transitions=['cancelar_confirmacao', 'finalizar_confirmacao'])
    stateDef.setPermission('Modify portal content',
                           0,
                           ['Anonymous', 'Owner', 'Manager'])

    ## Transitions initialization

    ## Creation of workflow scripts
    for wf_scriptname in ['enviaEmailConfirmacao']:
        if not wf_scriptname in workflow.scripts.objectIds():
            workflow.scripts._setObject(wf_scriptname,
                ExternalMethod(wf_scriptname, wf_scriptname,
                productname + '.inscricao_workflow_scripts',
                wf_scriptname))

    transitionDef = workflow.transitions['finalizar_confirmacao']
    transitionDef.setProperties(title="""Finalizar Confirmação""",
                                new_state_id="""registrado""",
                                trigger_type=1,
                                script_name="""""",
                                after_script_name="""enviaEmailConfirmacao""",
                                actbox_name="""Finalizar Confirmação""",
                                actbox_url="""""",
                                actbox_category="""workflow""",
                                props={},
                                )

    ## Creation of workflow scripts
    for wf_scriptname in ['marcaComoPaga']:
        if not wf_scriptname in workflow.scripts.objectIds():
            workflow.scripts._setObject(wf_scriptname,
                ExternalMethod(wf_scriptname, wf_scriptname,
                productname + '.inscricao_workflow_scripts',
                wf_scriptname))

    transitionDef = workflow.transitions['pagar']
    transitionDef.setProperties(title="""Pagar a inscrição""",
                                new_state_id="""registrado""",
                                trigger_type=1,
                                script_name="""""",
                                after_script_name="""marcaComoPaga""",
                                actbox_name="""Pagar a inscrição""",
                                actbox_url="""""",
                                actbox_category="""workflow""",
                                props={'guard_expr': 'not:object/getPaga', 'guard_roles': 'Manager'},
                                )

    transitionDef = workflow.transitions['registrar']
    transitionDef.setProperties(title="""Registrar inscrição""",
                                new_state_id="""registrado""",
                                trigger_type=1,
                                script_name="""""",
                                after_script_name="""""",
                                actbox_name="""Registrar inscrição""",
                                actbox_url="""""",
                                actbox_category="""workflow""",
                                props={},
                                )

    transitionDef = workflow.transitions['iniciar_confirmacao']
    transitionDef.setProperties(title="""Iniciar Confirmação""",
                                new_state_id="""em_confirmacao""",
                                trigger_type=1,
                                script_name="""""",
                                after_script_name="""""",
                                actbox_name="""Iniciar Confirmação""",
                                actbox_url="""""",
                                actbox_category="""workflow""",
                                props={'guard_expr': 'container/emInscricao'},
                                )

    ## Creation of workflow scripts
    for wf_scriptname in ['enviaEmailConfirmacao']:
        if not wf_scriptname in workflow.scripts.objectIds():
            workflow.scripts._setObject(wf_scriptname,
                ExternalMethod(wf_scriptname, wf_scriptname,
                productname + '.inscricao_workflow_scripts',
                wf_scriptname))

    transitionDef = workflow.transitions['confirmar']
    transitionDef.setProperties(title="""Confirmar a inscrição""",
                                new_state_id="""registrado""",
                                trigger_type=1,
                                script_name="""""",
                                after_script_name="""enviaEmailConfirmacao""",
                                actbox_name="""Confirmar a inscrição""",
                                actbox_url="""""",
                                actbox_category="""workflow""",
                                props={'guard_roles': 'Manager; Owner'},
                                )

    transitionDef = workflow.transitions['salvar']
    transitionDef.setProperties(title="""Salvar inscrição""",
                                new_state_id="""pre-inscrito""",
                                trigger_type=1,
                                script_name="""""",
                                after_script_name="""""",
                                actbox_name="""Salvar inscrição""",
                                actbox_url="""""",
                                actbox_category="""workflow""",
                                props={},
                                )

    transitionDef = workflow.transitions['cancelar_confirmacao']
    transitionDef.setProperties(title="""cancelar_confirmacao""",
                                new_state_id="""pre-inscrito""",
                                trigger_type=1,
                                script_name="""""",
                                after_script_name="""""",
                                actbox_name="""cancelar_confirmacao""",
                                actbox_url="""""",
                                actbox_category="""workflow""",
                                props={},
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



def createinscricao_workflow(self, id):
    """Create the workflow for PyConBrasil.
    """

    ob = DCWorkflowDefinition(id)
    setupinscricao_workflow(self, ob)
    return ob

addWorkflowFactory(createinscricao_workflow,
                   id='inscricao_workflow',
                   title='inscricao_workflow')

##code-section create-workflow-module-footer #fill in your manual code here
##/code-section create-workflow-module-footer

