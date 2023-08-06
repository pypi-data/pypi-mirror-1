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

readme_file= os.path.join('Products', 'qRSS2Syndication', 'README.txt')
long_desc = open(readme_file).read().strip()
version = '0.5.1'


setup(name='Products.qRSS2Syndication',
      version=version,
      author='Quintagroup',
      maintainer='Andreas Jung',
      maintainer_email='info@zopyx.com',
      classifiers=CLASSIFIERS,
      url='http://pypi.python.org/pypi/Products.qRSS2Syndication',
      description='Extended syndication support for Plone 3',
      long_description=long_desc,
      packages=['Products', 'Products.qRSS2Syndication'],
      include_package_data = True,
      zip_safe=False,
      install_requires=['setuptools'],
      namespace_packages=['Products'],

      )
