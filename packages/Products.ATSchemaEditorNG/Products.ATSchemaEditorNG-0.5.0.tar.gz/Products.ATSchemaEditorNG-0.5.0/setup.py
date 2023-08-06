##########################################################################
# ATSchemaEditorNG
# (C) 2007, 2008, ZOPYX Ltd & Co. KG, Tuebingen, Germany
##########################################################################

import os
from setuptools import setup, find_packages


CLASSIFIERS = [
    'Programming Language :: Python',
    'Framework :: Zope2',
    'Framework :: Plone',
]

version_file = os.path.join('Products', 'ATSchemaEditorNG', 'VERSION.txt')
version = open(version_file).read().strip()

readme_file= os.path.join('Products', 'ATSchemaEditorNG', 'README.txt')
desc = open(readme_file).read().strip()
changes_file = os.path.join('Products', 'ATSchemaEditorNG', 'doc', 'CHANGES.txt')
changes = open(changes_file).read().strip()

long_description = desc + '\n\nCHANGES\n=======\n\n' +  changes 

setup(name='Products.ATSchemaEditorNG',
      version=version,
      license='LGPL 3',
      author='Andreas Jung, Simon Pamies',
      author_email='info@zopyx.com',
      maintainer='Simon Pamies',
      maintainer_email='s.pamies@banality.de',
      classifiers=CLASSIFIERS,
      keywords='ArchetypesPlone Zope Python', 
      url='http://pypi.python.org/pypi/Products.ATSchemaEditorNG',
      description='Throught-web-editor for Archetype schemas',
      long_description=long_description,
      packages=['Products', 'Products.ATSchemaEditorNG'],
      include_package_data = True,
      zip_safe=False,
      namespace_packages=['Products'],

      )
