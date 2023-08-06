# -*- coding: utf-8 -*-
"""
This module contains the tool of collective.recipe.funkload
"""
import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '0.2'
long_description = (
    open(os.path.join("src", "collective", "recipe", "funkload",
        "README.txt")).read()
    + '\n' +
    'Change history\n'
    '**************\n'
    + '\n' +
    open('CHANGES.txt').read()
    + '\n' +
    'Contributors\n'
    '**************\n'
    + '\n' +
    open('CONTRIBUTORS.txt').read()
    + '\n' +
    'Download\n'
    '********\n')

tests_require=['zope.testing', 'zc.buildout']

setup(name='collective.recipe.funkload',
      version=version,
      description="Makes installing funkload, running tests and generating "
        "reports a 'no-brainer'",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Framework :: Buildout',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: Zope Public License',
        ],
      keywords='funkload recipe',
      author='Alan Hoey',
      author_email='alan.hoey@teamrubber.com',
      url='http://pypi.python.org/pypi/collective.recipe.funkload',
      license='ZPL',
      packages=find_packages('src', exclude=['ez_setup']),
      package_dir = {'':'src'},
      namespace_packages=['collective', 'collective.recipe'],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'zc.buildout',
                        'funkload',
                        'zc.recipe.egg',
                        ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      test_suite = 'collective.recipe.funkload.tests.test_docs.test_suite',
      entry_points={
           'console_scripts': ['funkload = collective.recipe.funkload.dispatcher:main'],
           'zc.buildout': ['default = collective.recipe.funkload:TestRunner'],
           },
      )
