##########################################################################
# SmartPrintNG
# (C) 2007, 2008, ZOPYX Ltd & Co. KG, Tuebingen, Germany
##########################################################################

import os
from setuptools import setup, find_packages


CLASSIFIERS = [
    'Programming Language :: Python',
    'Framework :: Zope2',
    'Framework :: Plone',
]

version_file = os.path.join('Products', 'SmartPrintNG', 'version.txt')
version = open(version_file).read().strip()

readme_file= os.path.join('Products', 'SmartPrintNG', 'README.txt')
desc = open(readme_file).read().strip()
changes_file = os.path.join('Products', 'SmartPrintNG', 'CHANGES.txt')
changes = open(changes_file).read().strip()

long_description = desc + '\n\nCHANGES\n=======\n\n' +  changes 

setup(name='Products.SmartPrintNG',
      version=version,
      license='LGPL 3',
      author='Andreas Jung',
      author_email='info@zopyx.com',
      maintainer='Andreas Jung',
      maintainer_email='info@zopyx.com',
      classifiers=CLASSIFIERS,
      keywords='PDF  RTF  ODT  DOCX  WML conversion Plone Zope Python', 
      url='http://opensource.zopyx.com/projects/SmartPrintNG',
      description='Conversion of Plone content to PDF, RTS, ODT, DOCX and WML',
      long_description=long_description,
      packages=['Products', 'Products.SmartPrintNG'],
      include_package_data = True,
      zip_safe=False,
      install_requires=['setuptools', 'zopyx.convert>=1.1.7'],
      namespace_packages=['Products'],

      )
