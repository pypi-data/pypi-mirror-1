##########################################################################
# Products.upaCore
# (C) 2007, 2008, ZOPYX Ltd & Co. KG, Tuebingen, Germany
##########################################################################

import os
from setuptools import setup, find_packages


CLASSIFIERS = [
    'Programming Language :: Python',
    'Framework :: Zope2',
    'Framework :: Plone',
]

version =  '0.5.1.4'

readme_file= os.path.join('Products', 'upaCore', 'README.txt')
desc = open(readme_file).read().strip()
changes_file = os.path.join('docs', 'HISTORY.txt')
changes = open(changes_file).read().strip()

long_description = desc + '\n\nCHANGES\n=======\n\n' +  changes 

setup(name='Products.upaCore',
      version=version,
      license='GPL',
      author='Andreas Jung',
      author_email='info@zopyx.com',
      maintainer='Andreas Jung',
      maintainer_email='info@zopyx.com',
      classifiers=CLASSIFIERS,
      url='http://pypi.python.org/pypi/Products.upaCore',
      description='Member info implementation for the GermanUPA',
      long_description=long_description,
      packages=['Products', 'Products.upaCore'],
      include_package_data = True,
      zip_safe=False,
      install_requires=['setuptools', 'archetypes.schemaextender', 'Products.TrustedExecutables'],
      namespace_packages=['Products'],
      )
