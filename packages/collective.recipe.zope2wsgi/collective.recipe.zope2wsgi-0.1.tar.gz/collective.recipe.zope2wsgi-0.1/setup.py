# -*- coding: utf-8 -*-
"""
This module contains the tool of collective.recipe.zope2wsgi
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
    read('collective', 'recipe', 'zope2wsgi', 'README.txt')
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

tests_require=['zope.testing', 'zc.buildout']

setup(name='collective.recipe.zope2wsgi',
      version=version,
      description="zc.buildout recipe to generate zope instances using repoze.zope2",
      long_description=long_description,
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        'Framework :: Buildout',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: Zope Public License',
        'Development Status :: 4 - Beta',
        'Framework :: Zope2',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        ],
      keywords='wsgi zope2 buildout',
      author='Gael Pasgrimaud',
      author_email='gael@gawel.org',
      url='http://pypi.python.org/pypi/collective.recipe.zope2wsgi',
      license='ZPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['collective', 'collective.recipe'],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        'zc.buildout',
                        'zc.recipe.egg',
                        'repoze.zope2',
                        'PasteScript',
                        'WebError',
                        'plone.recipe.zope2instance',
                        'plone.recipe.zope2zeoserver',
                        ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      test_suite = 'collective.recipe.zope2wsgi.tests.test_docs.test_suite',
      entry_points="""
      [zc.buildout]
      default = collective.recipe.zope2wsgi:Instance
      zeo = collective.recipe.zope2wsgi:Server
      [console_scripts]
      paster_serve = collective.recipe.zope2wsgi.scripts:serve
      mod_wsgi = collective.recipe.zope2wsgi.scripts:mod_wsgi
      """
      )
