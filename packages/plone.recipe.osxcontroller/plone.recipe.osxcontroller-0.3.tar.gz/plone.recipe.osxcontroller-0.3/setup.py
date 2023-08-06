# -*- coding: utf-8 -*-
"""
This module contains the tool of plone.recipe.osxcontroller
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '0.3'

long_description = (
    read('README.txt')
    + '\n' +
    'Detailed Documentation\n'
    '**********************\n'
    + '\n' +
    read('plone', 'recipe', 'osxcontroller', 'README.txt')
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
    + '\n'
    )
entry_point = 'plone.recipe.osxcontroller:Recipe'
entry_points = {"zc.buildout": ["default = %s" % entry_point]}

tests_require=['zope.testing', 'zc.buildout']

setup(name='plone.recipe.osxcontroller',
      version=version,
      description="Installs a wxPython-based Plone controller for OS X",
      long_description=long_description,
      classifiers=[
        'Framework :: Buildout',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: Zope Public License',
        ],
      keywords='plone',
      author='Steve McMahon',
      author_email='steve@dcn.org',
      url='http://plone.org/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['plone', 'plone.recipe'],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'zc.buildout'
                        # -*- Extra requirements: -*-
                        ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      test_suite = 'plone.recipe.osxcontroller.tests.test_docs.test_suite',
      entry_points=entry_points,
      )
