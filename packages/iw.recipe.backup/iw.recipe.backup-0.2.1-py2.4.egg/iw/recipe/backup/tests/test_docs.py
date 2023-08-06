# -*- coding: utf-8 -*-
"""
Doctest runner for 'iw.recipe.backup'.
"""
__docformat__ = 'restructuredtext'

import os
import re
import unittest
import zc.buildout.tests
import zc.buildout.testing

from zope.testing import doctest, renormalizing

optionflags =  (doctest.ELLIPSIS |
                doctest.NORMALIZE_WHITESPACE |
                doctest.REPORT_ONLY_FIRST_FAILURE)

test_dir = os.path.dirname(__file__)

def setUp(test):
    zc.buildout.testing.buildoutSetUp(test)

    # Install the recipe in develop mode
    zc.buildout.testing.install_develop('iw.recipe.backup', test)

    # Install any other recipes that should be available in the tests
    #zc.buildout.testing.install('collective.recipe.foobar', test)

def tearDown(test):
    from iw.recipe.backup import testing
    testing.remove_input()
    zc.buildout.testing.buildoutTearDown(test)

def test_suite():

    suite = unittest.TestSuite((
            doctest.DocFileSuite(
                '../README.txt',
                setUp=setUp,
                tearDown=tearDown,
                optionflags=optionflags,
                globs=globals(),
                checker=renormalizing.RENormalizing([
                        # If want to clean up the doctest output you
                        # can register additional regexp normalizers
                        # here. The format is a two-tuple with the RE
                        # as the first item and the replacement as the
                        # second item, e.g.
                        # (re.compile('my-[rR]eg[eE]ps'), 'my-regexps')
                        (re.compile('-[0-9]{4}'), '-XXXX'),
                        (re.compile('-[0-9]{2}'), '-XX'),
                        zc.buildout.testing.normalize_path,
                        ]),
                ),
            ))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
