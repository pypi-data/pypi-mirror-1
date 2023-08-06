# -*- coding: utf-8 -*-
"""
This module contains the tool of gocept.recipe.deploymentsandbox
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '0.2'

long_description = (
    read('README.txt')
    + '\n' +
    'Change history\n'
    '**************\n'
    + '\n' + 
    read('CHANGES.txt')
    + '\n' +
    'Detailed Documentation\n'
    '**********************\n'
    + '\n' +
    read('gocept', 'recipe', 'deploymentsandbox', 'README.txt')
    + '\n' +
    'Contributors\n' 
    '************\n'
    + '\n' +
    read('CONTRIBUTORS.txt')
    + '\n' +
    'Download\n'
    '********\n'
    )
entry_point = 'gocept.recipe.deploymentsandbox:Recipe'
entry_points = {"zc.buildout": ["default = %s" % entry_point]}

setup(name='gocept.recipe.deploymentsandbox',
      version=version,
      description="Setup a sandbox environment for deployments based on zc.recipe.deployment",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Framework :: Buildout',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: Zope Public License',
        ],
      keywords='',
      author='Christian Theune',
      author_email='ct@gocept.com',
      url='http://pypi.python.org/pypi/gocept.recipe.deploymentsandbox',
      license='ZPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['gocept', 'gocept.recipe'],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'zc.buildout'
                        # -*- Extra requirements: -*-
                        ],
      extras_require=dict(test=['zope.testing',]),
      test_suite = 'gocept.recipe.deploymentsandbox.tests.test_docs.test_suite',
      entry_points=entry_points,
      )
