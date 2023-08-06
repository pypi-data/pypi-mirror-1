# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import os

version = open(os.path.join("Products", "PyConBrasil", "version.txt")).read().strip()

setup(name='Products.PyConBrasil',
      version=version,
      description="Produto para gerenciamento de trabalhos e inscricoes para a PyConBrasil",
      long_description=open(os.path.join("Products", "PyConBrasil", "README.txt")).read().decode('UTF8').encode('ASCII', 'replace'),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Plone",
        "Framework :: Zope2"
        ],
      keywords='pyconbrasil plone zope registration',
      author='APyB - Associacao Python Brasil',
      author_email='contato@pythobrasil.com.br',
      url='http://svn.plone.org/svn/collective/Products.PyConBrasil/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-,
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
