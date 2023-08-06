# -*- coding: utf-8 -*-
"""
Doctest runner for 'collective.recipe.zope2wsgi'.
"""
__docformat__ = 'restructuredtext'

import unittest
import zc.buildout.tests
import zc.buildout.testing

from zope.testing import doctest, renormalizing

optionflags =  (doctest.ELLIPSIS |
                doctest.NORMALIZE_WHITESPACE |
                doctest.REPORT_ONLY_FIRST_FAILURE)

def setUp(test):
    zc.buildout.testing.buildoutSetUp(test)

    # Install the recipe in develop mode
    zc.buildout.testing.install_develop('collective.recipe.zope2wsgi', test)

    # Install any other recipes that should be available in the tests
    zc.buildout.testing.install_develop('plone.recipe.zope2zeoserver', test)
    zc.buildout.testing.install_develop('plone.recipe.zope2instance', test)
    zc.buildout.testing.install_develop('zc.recipe.egg', test)
    zc.buildout.testing.install_develop('repoze.zope2', test)
    zc.buildout.testing.install_develop('repoze.errorlog', test)
    zc.buildout.testing.install_develop('repoze.obob', test)
    zc.buildout.testing.install_develop('repoze.vhm', test)
    zc.buildout.testing.install_develop('repoze.retry', test)
    zc.buildout.testing.install_develop('repoze.tm', test)
    zc.buildout.testing.install_develop('zopelib', test)
    zc.buildout.testing.install_develop('WSGIUtils', test)
    zc.buildout.testing.install_develop('Paste', test)
    zc.buildout.testing.install_develop('PasteScript', test)
    zc.buildout.testing.install_develop('PasteDeploy', test)
    zc.buildout.testing.install_develop('WebError', test)
    zc.buildout.testing.install_develop('simplejson', test)
    zc.buildout.testing.install_develop('elementtree', test)
    zc.buildout.testing.install_develop('meld3', test)
    zc.buildout.testing.install_develop('ZODB3', test)
    zc.buildout.testing.install_develop('zdaemon', test)
    zc.buildout.testing.install_develop('ZConfig', test)
    zc.buildout.testing.install_develop('Pygments', test)
    zc.buildout.testing.install_develop('Tempita', test)
    zc.buildout.testing.install_develop('WebOb', test)
    zc.buildout.testing.install_develop('zope.testing', test)
    zc.buildout.testing.install_develop('zope.proxy', test)
    zc.buildout.testing.install_develop('zope.interface', test)

def test_suite():
    suite = unittest.TestSuite((
            doctest.DocFileSuite(
                '../README.txt',
                setUp=setUp,
                tearDown=zc.buildout.testing.buildoutTearDown,
                optionflags=optionflags,
                checker=renormalizing.RENormalizing([
                        # If want to clean up the doctest output you
                        # can register additional regexp normalizers
                        # here. The format is a two-tuple with the RE
                        # as the first item and the replacement as the
                        # second item, e.g.
                        # (re.compile('my-[rR]eg[eE]ps'), 'my-regexps')
                        zc.buildout.testing.normalize_path,
                        ]),
                ),
            ))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
