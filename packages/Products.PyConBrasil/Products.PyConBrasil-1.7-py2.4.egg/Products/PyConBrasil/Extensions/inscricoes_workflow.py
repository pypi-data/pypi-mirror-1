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

def setupinscricoes_workflow(self, workflow):
    """Define the inscricoes_workflow workflow.
    """

    workflow.setProperties(title='inscricoes_workflow')

    ##code-section create-workflow-setup-method-header #fill in your manual code here
    ##/code-section create-workflow-setup-method-header


    for s in ['fechado', 'pre-inscricoes', 'inscricoes', 'encerrado', 'todos']:
        workflow.states.addState(s)

    for t in ['encerrar', 'fechar', 'abrir_todos', 'abrir_inscricoes', 'abrir_pre-inscricoes']:
        workflow.transitions.addTransition(t)

    for v in ['review_history', 'comments', 'time', 'actor', 'action']:
        workflow.variables.addVariable(v)

    workflow.addManagedPermission('PyConBrasil: Add Imprensa')
    workflow.addManagedPermission('PyConBrasil: Add Inscricao')
    workflow.addManagedPermission('PyConBrasil: Add Palestra')
    workflow.addManagedPermission('PyConBrasil: Add PalestraRelampago')
    workflow.addManagedPermission('PyConBrasil: Add Treinamento')
    workflow.addManagedPermission('View')
    workflow.addManagedPermission('Modify portal content')
    workflow.addManagedPermission('Add portal content')
    workflow.addManagedPermission('Access contents information')

    for l in []:
        if not l in workflow.worklists.objectValues():
            workflow.worklists.addWorklist(l)

    ## Initial State

    workflow.states.setInitialState('fechado')

    ## States initialization

    stateDef = workflow.states['fechado']
    stateDef.setProperties(title="""Fechado""",
                           description="""""",
                           transitions=['abrir_pre-inscricoes', 'abrir_todos'])
    stateDef.setPermission('PyConBrasil: Add Imprensa',
                           0,
                           ['Manager', 'Owner'])
    stateDef.setPermission('PyConBrasil: Add Inscricao',
                           0,
                           ['Manager', 'Owner'])
    stateDef.setPermission('PyConBrasil: Add Palestra',
                           0,
                           ['Manager', 'Owner'])
    stateDef.setPermission('PyConBrasil: Add PalestraRelampago',
                           0,
                           ['Manager', 'Owner'])
    stateDef.setPermission('PyConBrasil: Add Treinamento',
                           0,
                           ['Manager', 'Owner'])
    stateDef.setPermission('View',
                           0,
                           ['Anonymous', 'Member', 'Manager', 'Owner'])
    stateDef.setPermission('Modify portal content',
                           0,
                           ['Manager', 'Owner'])
    stateDef.setPermission('Add portal content',
                           0,
                           ['Manager', 'Owner'])
    stateDef.setPermission('Access contents information',
                           0,
                           ['Anonymous', 'Member', 'Manager', 'Owner'])

    stateDef = workflow.states['pre-inscricoes']
    stateDef.setProperties(title="""Chamada de trabalhos""",
                           description="""""",
                           transitions=['abrir_inscricoes'])
    stateDef.setPermission('PyConBrasil: Add Imprensa',
                           0,
                           ['Manager'])
    stateDef.setPermission('PyConBrasil: Add Inscricao',
                           0,
                           ['Manager'])
    stateDef.setPermission('PyConBrasil: Add Palestra',
                           0,
                           ['Anonymous', 'Member', 'Manager', 'Owner'])
    stateDef.setPermission('PyConBrasil: Add PalestraRelampago',
                           0,
                           ['Anonymous', 'Member', 'Manager', 'Owner'])
    stateDef.setPermission('PyConBrasil: Add Treinamento',
                           0,
                           ['Anonymous', 'Member', 'Manager', 'Owner'])
    stateDef.setPermission('View',
                           0,
                           ['Anonymous', 'Member', 'Manager', 'Owner'])
    stateDef.setPermission('Modify portal content',
                           0,
                           ['Anonymous', 'Member', 'Manager', 'Owner'])
    stateDef.setPermission('Add portal content',
                           0,
                           ['Anonymous', 'Member', 'Manager', 'Owner'])
    stateDef.setPermission('Access contents information',
                           0,
                           ['Anonymous', 'Member', 'Manager', 'Owner'])

    stateDef = workflow.states['inscricoes']
    stateDef.setProperties(title="""Somente inscrições abertas""",
                           description="""""",
                           transitions=['fechar', 'encerrar'])
    stateDef.setPermission('PyConBrasil: Add Imprensa',
                           0,
                           ['Anonymous', 'Member', 'Manager', 'Owner'])
    stateDef.setPermission('PyConBrasil: Add Inscricao',
                           0,
                           ['Anonymous', 'Member', 'Manager', 'Owner'])
    stateDef.setPermission('PyConBrasil: Add Palestra',
                           0,
                           ['Manager', 'Owner'])
    stateDef.setPermission('PyConBrasil: Add PalestraRelampago',
                           0,
                           ['Manager', 'Owner'])
    stateDef.setPermission('PyConBrasil: Add Treinamento',
                           0,
                           ['Manager', 'Owner'])
    stateDef.setPermission('Add portal content',
                           0,
                           ['Anonymous', 'Member', 'Manager', 'Owner'])
    stateDef.setPermission('View',
                           0,
                           ['Anonymous', 'Member', 'Manager', 'Owner'])
    stateDef.setPermission('Modify portal content',
                           0,
                           ['Manager', 'Owner'])
    stateDef.setPermission('Access contents information',
                           0,
                           ['Anonymous', 'Member', 'Manager', 'Owner'])

    stateDef = workflow.states['encerrado']
    stateDef.setProperties(title="""Inscrições encerradas""",
                           description="""""",
                           transitions=[])
    stateDef.setPermission('PyConBrasil: Add Imprensa',
                           0,
                           [])
    stateDef.setPermission('PyConBrasil: Add Inscricao',
                           0,
                           [])
    stateDef.setPermission('PyConBrasil: Add Palestra',
                           0,
                           [])
    stateDef.setPermission('PyConBrasil: Add PalestraRelampago',
                           0,
                           [])
    stateDef.setPermission('PyConBrasil: Add Treinamento',
                           0,
                           [])
    stateDef.setPermission('View',
                           0,
                           ['Anonymous', 'Member', 'Manager', 'Owner'])
    stateDef.setPermission('Modify portal content',
                           0,
                           ['Manager', 'Owner'])
    stateDef.setPermission('Add portal content',
                           0,
                           [])
    stateDef.setPermission('Access contents information',
                           0,
                           ['Anonymous', 'Member', 'Manager', 'Owner'])

    stateDef = workflow.states['todos']
    stateDef.setProperties(title="""Todas as inscrições abertas""",
                           description="""""",
                           transitions=['encerrar', 'fechar'])
    stateDef.setPermission('PyConBrasil: Add Imprensa',
                           0,
                           ['Anonymous', 'Member', 'Manager', 'Owner'])
    stateDef.setPermission('PyConBrasil: Add Inscricao',
                           0,
                           ['Anonymous', 'Member', 'Manager', 'Owner'])
    stateDef.setPermission('PyConBrasil: Add Palestra',
                           0,
                           ['Anonymous', 'Member', 'Manager', 'Owner'])
    stateDef.setPermission('PyConBrasil: Add PalestraRelampago',
                           0,
                           ['Anonymous', 'Member', 'Manager', 'Owner'])
    stateDef.setPermission('PyConBrasil: Add Treinamento',
                           0,
                           ['Anonymous', 'Member', 'Manager', 'Owner'])
    stateDef.setPermission('View',
                           0,
                           ['Anonymous', 'Member', 'Manager', 'Owner'])
    stateDef.setPermission('Modify portal content',
                           0,
                           ['Manager', 'Owner'])
    stateDef.setPermission('Add portal content',
                           0,
                           ['Anonymous', 'Member', 'Manager', 'Owner'])
    stateDef.setPermission('Access contents information',
                           0,
                           ['Anonymous', 'Member', 'Manager', 'Owner'])

    ## Transitions initialization

    transitionDef = workflow.transitions['encerrar']
    transitionDef.setProperties(title="""Encerrar inscrições""",
                                new_state_id="""encerrado""",
                                trigger_type=1,
                                script_name="""""",
                                after_script_name="""""",
                                actbox_name="""Encerrar inscrições""",
                                actbox_url="""""",
                                actbox_category="""workflow""",
                                props={'guard_roles': 'Manager; Owner'},
                                )

    transitionDef = workflow.transitions['fechar']
    transitionDef.setProperties(title="""Cancelar inscrições""",
                                new_state_id="""fechado""",
                                trigger_type=1,
                                script_name="""""",
                                after_script_name="""""",
                                actbox_name="""Cancelar inscrições""",
                                actbox_url="""""",
                                actbox_category="""workflow""",
                                props={'guard_roles': 'Manager; Owner'},
                                )

    transitionDef = workflow.transitions['abrir_todos']
    transitionDef.setProperties(title="""Abrir todas as inscrições""",
                                new_state_id="""todos""",
                                trigger_type=1,
                                script_name="""""",
                                after_script_name="""""",
                                actbox_name="""Abrir todas as inscrições""",
                                actbox_url="""""",
                                actbox_category="""workflow""",
                                props={'guard_roles': 'Manager; Owner'},
                                )

    ## Creation of workflow scripts
    for wf_scriptname in ['enviaEmailPreInscritos']:
        if not wf_scriptname in workflow.scripts.objectIds():
            workflow.scripts._setObject(wf_scriptname,
                ExternalMethod(wf_scriptname, wf_scriptname,
                productname + '.inscricoes_workflow_scripts',
                wf_scriptname))

    transitionDef = workflow.transitions['abrir_inscricoes']
    transitionDef.setProperties(title="""Abrir inscrições""",
                                new_state_id="""inscricoes""",
                                trigger_type=1,
                                script_name="""""",
                                after_script_name="""enviaEmailPreInscritos""",
                                actbox_name="""Abrir inscrições""",
                                actbox_url="""""",
                                actbox_category="""workflow""",
                                props={'guard_roles': 'Manager; Owner'},
                                )

    transitionDef = workflow.transitions['abrir_pre-inscricoes']
    transitionDef.setProperties(title="""Abrir pré-inscrições""",
                                new_state_id="""pre-inscricoes""",
                                trigger_type=1,
                                script_name="""""",
                                after_script_name="""""",
                                actbox_name="""Abrir pré-inscrições""",
                                actbox_url="""""",
                                actbox_category="""workflow""",
                                props={'guard_roles': 'Manager; Owner'},
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



def createinscricoes_workflow(self, id):
    """Create the workflow for PyConBrasil.
    """

    ob = DCWorkflowDefinition(id)
    setupinscricoes_workflow(self, ob)
    return ob

addWorkflowFactory(createinscricoes_workflow,
                   id='inscricoes_workflow',
                   title='inscricoes_workflow')

##code-section create-workflow-module-footer #fill in your manual code here
##/code-section create-workflow-module-footer

