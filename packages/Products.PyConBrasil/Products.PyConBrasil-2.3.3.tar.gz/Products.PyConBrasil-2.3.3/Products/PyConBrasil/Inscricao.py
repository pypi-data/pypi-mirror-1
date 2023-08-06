# -*- coding: utf-8 -*-
#
# File: Inscricao.py
#
# Copyright (c) 2007 by Associação Python Brasil
# Generator: ArchGenXML 
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

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from Products.PyConBrasil.UIDRenamer import UIDRenamer
from Products.PyConBrasil.config import *

##code-section module-header #fill in your manual code here
import transaction
from Products.CMFCore.utils import getToolByName
##/code-section module-header

schema = Schema((

    StringField(
        name='nome',
        widget=StringWidget(
            description="Informe o seu nome completo.",
            label='Nome',
            label_msgid='PyConBrasil_label_nome',
            description_msgid='PyConBrasil_help_nome',
            i18n_domain='PyConBrasil',
        ),
        required=1
    ),

    StringField(
        name='sexo',
        widget=SelectionWidget(
            description="Informe o seu sexo.",
            label='Sexo',
            label_msgid='PyConBrasil_label_sexo',
            description_msgid='PyConBrasil_help_sexo',
            i18n_domain='PyConBrasil',
        ),
        enforceVocabulary=1,
        vocabulary=['Feminino', 'Masculino'],
        required=1
    ),

    StringField(
        name='email',
        widget=StringWidget(
            label="E-Mail",
            description="Informe o seu endereço eletrônico.",
            label_msgid='PyConBrasil_label_email',
            description_msgid='PyConBrasil_help_email',
            i18n_domain='PyConBrasil',
        ),
        required=1,
        validators=('isEmail',)
    ),

    StringField(
        name='telefone',
        widget=StringWidget(
            description="Informe o seu telefone para contato em caso de necessidade. Incluindo o código DDD.",
            size=14,
            maxlength=20,
            label='Telefone',
            label_msgid='PyConBrasil_label_telefone',
            description_msgid='PyConBrasil_help_telefone',
            i18n_domain='PyConBrasil',
        )
    ),

    StringField(
        name='cidade',
        widget=StringWidget(
            description="Informe o nome da cidade em que você reside.",
            label='Cidade',
            label_msgid='PyConBrasil_label_cidade',
            description_msgid='PyConBrasil_help_cidade',
            i18n_domain='PyConBrasil',
        ),
        required=1
    ),

    StringField(
        name='estado',
        widget=SelectionWidget(
            description="Selecione o Estado em que você reside.",
            label='Estado',
            label_msgid='PyConBrasil_label_estado',
            description_msgid='PyConBrasil_help_estado',
            i18n_domain='PyConBrasil',
        ),
        enforceVocabulary=1,
        vocabulary=ESTADOS,
        required=1
    ),

    StringField(
        name='endereco',
        widget=StringWidget(
            description="Informe o endereço completo em que você reside. Será utilizado caso seja necessário enviar algo para você como por exemplo o certificado de participação.",
            condition="not:object/emPreInscricao",
            label="Endereço",
            label_msgid='PyConBrasil_label_endereco',
            description_msgid='PyConBrasil_help_endereco',
            i18n_domain='PyConBrasil',
        )
    ),

    StringField(
        name='instituicao',
        widget=StringWidget(
            description="Informe o nome da instituição em que você estuda, trabalha ou representa.",
            condition="not:object/emPreInscricao",
            label="Instituição",
            label_msgid='PyConBrasil_label_instituicao',
            description_msgid='PyConBrasil_help_instituicao',
            i18n_domain='PyConBrasil',
        )
    ),

    StringField(
        name='tipo',
        widget=SelectionWidget(
            description="Tipo da inscrição que está sendo realizada.",
            condition="not:object/emPreInscricao",
            label='Tipo',
            label_msgid='PyConBrasil_label_tipo',
            description_msgid='PyConBrasil_help_tipo',
            i18n_domain='PyConBrasil',
        ),
        required=1,
        vocabulary=(
            ('1', 'Estudante ou Membro APyB'),
            ('2', 'Membro SBC ou Membro ABRAWEB'),
            ('3', 'Público em geral'),
            ('4', 'Patrocinador'),
        ),
    ),

    BooleanField(
        name='paga',
        widget=BooleanWidget(
            visible=0,
            label='Paga',
            label_msgid='PyConBrasil_label_paga',
            i18n_domain='PyConBrasil',
        )
    ),

    ReferenceField(
        name='treinamentos',
        widget=ReferenceWidget(
            description="Selecione os treinamentos que você deseja participar.",
            format="select",
            visible=0,
            condition="not:object/emPreInscricao",
            label='Treinamentos',
            label_msgid='PyConBrasil_label_treinamentos',
            description_msgid='PyConBrasil_help_treinamentos',
            i18n_domain='PyConBrasil',
        ),
        allowed_types=('Treinamento',),
        multiValued=1,
        relationship='Inscricao_Treinamento'
    ),

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

Inscricao_schema = BaseSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here

Inscricao_schema['title'].required = 0
Inscricao_schema['title'].widget.visible = {'view':'invisible', 'edit':'invisible'}

##/code-section after-schema

class Inscricao(UIDRenamer, BaseContent):
    """Inscricao efetiva do participante do evento.
    """
    security = ClassSecurityInfo()
    __implements__ = (getattr(UIDRenamer,'__implements__',()),) + (getattr(BaseContent,'__implements__',()),)

    # This name appears in the 'add' box
    archetype_name = 'Inscrição'

    meta_type = 'Inscricao'
    portal_type = 'Inscricao'
    allowed_content_types = []
    filter_content_types = 0
    global_allow = 0
    content_icon = 'inscricao_icon.gif'
    immediate_view = 'base_view'
    default_view = 'base_view'
    suppl_views = ()
    typeDescription = "Inscrição de um participante no evento."
    typeDescMsgId = 'description_edit_inscricao'

    _at_rename_after_creation = True

    schema = Inscricao_schema
    for schemata in ['settings','categorization','metadata','dates','ownership']:
        for field in schema.getSchemataFields(schemata):
            field.widget.visible={'edit':'invisible','view':'invisible'}
    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods

    # Manually created methods

    def Title(self):
        """Retorna o nome como título do objeto.
        """
        return self.getNome()


def modify_fti(fti):
    # Hide unnecessary tabs (usability enhancement)
    for a in fti['actions']:
        if a['id'] in ['metadata', 'sharing']:
            a['visible'] = 0
    return fti

registerType(Inscricao, PROJECTNAME)
# end of class Inscricao

##code-section module-footer #fill in your manual code here
##/code-section module-footer



