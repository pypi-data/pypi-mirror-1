# -*- coding: utf-8 -*-
"""
This module contains the tool of zgeo.recipe.openlayers
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '0.1'

long_description = (
    read('README.txt')
    + '\n' +
    'Detailed Documentation\n'
    '**********************\n'
    + '\n' +
    read('zgeo', 'recipe', 'openlayers', 'README.txt')
    + '\n' +
    'Contributors\n' 
    '************\n'
    + '\n' +
    read('CONTRIBUTORS.txt')
    + '\n' +
    'Change history\n'
    '**************\n'
    + '\n' + 
    read('CHANGES.txt')
    + '\n' +
   'Download\n'
    '********\n'
    )
entry_point = 'zgeo.recipe.openlayers:Recipe'
entry_points = {"zc.buildout": ["default = %s" % entry_point]}

tests_require=['zope.testing', 'zc.buildout']

setup(name='zgeo.recipe.openlayers',
      version=version,
      description="Build standard or custom profiles of the OpenLayers library",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Framework :: Buildout',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        ],
      keywords='buildout recipe openlayers',
      author='Sean Gillies',
      author_email='sean.gillies@gmail.com',
      url='http://bitbucket.org/sgillies/zgeorecipeopenlayers/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['zgeo', 'zgeo.recipe'],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'zc.buildout',
                        'hexagonit.recipe.download'
                        # -*- Extra requirements: -*-
                        ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      test_suite = 'zgeo.recipe.openlayers.tests.test_docs.test_suite',
      entry_points=entry_points,
      )
