# -*- coding: utf-8 -*-
"""
This module contains the tool of iw.recipe.sendmail
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '0.2.3'

long_description = (
    read('README.txt')
    + '\n' +
    'Change history\n'
    '**************\n'
    + '\n' + 
    read('CHANGES')
    + '\n' +
    'Detailed Documentation\n'
    '**********************\n'
    + '\n' +
    read('iw', 'recipe', 'sendmail', 'README.txt')
    + '\n' +
    'Contributors\n' 
    '************\n'
    + '\n' +
    read('CONTRIBUTORS.txt')
    + '\n' +
    'Download\n'
    '********\n'
    )
entry_point = 'iw.recipe.sendmail:Recipe'
entry_points = {"zc.buildout": ["default = %s" % entry_point]}

tests_require=['zope.testing',
               'iw.recipe.template',
              ]

setup(name='iw.recipe.sendmail',
      version=version,
      description="ZC buildout recipe to setup zope.sendmail in a Zope2 instance",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Framework :: Buildout',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        ],
      keywords='plone zope smtp',
      author='Ingeniweb',
      author_email='support@ingeniweb.com',
      url='http://plone.org/products/iw-recipes',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['iw', 'iw.recipe'],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'zc.buildout',
                        # -*- Extra requirements: -*-
                        'iw.recipe.template',
                        ],
      tests_require=tests_require,
      extras_require=dict(test=tests_require),
      test_suite = 'iw.recipe.sendmail.tests.test_docs.test_suite',
      entry_points=entry_points,
      )
