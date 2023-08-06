# -*- coding: utf-8 -*-
"""
This module contains the tool of collective.recipe.solrinstance
"""
import os
from setuptools import setup, find_packages

version = '0.3'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

entry_point = 'collective.recipe.solrinstance:Recipe'

entry_points = {"zc.buildout": ["default = %s" % entry_point]}

setup(name='collective.recipe.solrinstance',
      version=version,
      description="zc.buildout to configure a solr instance",
      long_description= (
        read('README.txt')
        + '\n' +
        read('CHANGES.txt')
        + '\n' +
        'Contributors\n' 
        '***********************\n'
        + '\n' +
        read('CONTRIBUTORS.txt')
        + '\n' +
        'Download\n'
        '***********************\n'
        ),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Framework :: Buildout',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Zope Public License',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries :: Python Modules',
        ],
      keywords='',
      author='Kai Lautaportti',
      author_email='kai.lautaportti@hexagonit.fi',
      url='',
      license='ZPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.recipe'],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'iw.recipe.template',
                        'zc.buildout'
                        # -*- Extra requirements: -*-
                        ],
      tests_require=['zope.testing',
                     'iw.recipe.template',
                    ],
      test_suite = 'collective.recipe.solrinstance.tests.test_suite',
      entry_points=entry_points,
      )
