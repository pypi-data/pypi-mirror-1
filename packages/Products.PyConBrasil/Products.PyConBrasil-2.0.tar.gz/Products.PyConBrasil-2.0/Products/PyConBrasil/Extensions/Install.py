# -*- coding: utf-8 -*-

__author__ = """Jean Rodrigo Ferri / Dorneles Treméa / Fabiano Weimar / Rodrigo Senra /
Érico Andrei <contato@pythobrasil.com.br>"""
__docformat__ = 'plaintext'


__author__  = '''Simples Consultoria'''
__docformat__ = 'plaintext'

# Python imports
import StringIO
from cStringIO import StringIO
import string

from Products.CMFCore.utils import getToolByName
from Products.Archetypes import listTypes

# Config

def install(self):
    out=StringIO()
    
    setup_tool = getToolByName(self, 'portal_setup')
    
    setup_tool.runAllImportStepsFromProfile("profile-Products.PyConBrasil:default", purge_old=False)

    out.write('Installation completed.\n')
    return out.getvalue()

def uninstall(self):
    out=StringIO()
    return out.getvalue()

