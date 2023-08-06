##########################################################################
# ATBiblioStyles
# (C) 2007, 2008, ZOPYX Ltd & Co. KG, Tuebingen, Germany
##########################################################################

import os
from setuptools import setup, find_packages


CLASSIFIERS = [
    'Programming Language :: Python',
    'Framework :: Zope2',
    'Framework :: Plone',
]

version_file = os.path.join('Products', 'ATBiblioStyles', 'version.txt')
version = open(version_file).read().strip()

readme_file= os.path.join('Products', 'ATBiblioStyles', 'README.txt')
desc = open(readme_file).read().strip()
changes_file = os.path.join('docs', 'HISTORY.txt')
changes = open(changes_file).read().strip()

long_description = desc + '\n\nCHANGES\n=======\n\n' +  changes 

setup(name='Products.ATBiblioStyles',
      version=version,
      license='LGPL 3',
      author='David Convent',
      author_email='david.convent@naturalscience.be',
      maintainer='Andreas Jung',
      maintainer_email='info@zopyx.com',
      classifiers=CLASSIFIERS,
      keywords='CMFBibliographyAT',
      url='http://pypi.python.org/pypi/Products.ATBiblioStyles',
      description='Bibliography styles for CMFBibliographyAT',
      long_description=long_description,
      packages=['Products', 'Products.ATBiblioStyles'],
      include_package_data = True,
      zip_safe=False,
      install_requires=['setuptools', ],
      namespace_packages=['Products'],

      )
