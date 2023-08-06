# -*- coding: utf-8 -*-
"""
collective.recipe.libsvm

Licensed under the GPL license, see LICENCE.txt for more details.

$Id: event.py 67630 2006-04-27 00:54:03Z jfroche $

Doctest runner for 'collective.buildbot'.
"""
__docformat__ = 'restructuredtext'

from os.path import join
import unittest
import zc.buildout.testing

from zope.testing import doctest, renormalizing

optionflags = (doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE |
               doctest.REPORT_ONLY_FIRST_FAILURE)


def setUp(test):
    zc.buildout.testing.buildoutSetUp(test)
    zc.buildout.testing.install_develop('collective.recipe.libsvm', test)


def test_suite():

    # doc file suite
    test_files = ['README.txt']
    suite = unittest.TestSuite([
            doctest.DocFileSuite(
                join('..', filename),
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
                )
            for filename in test_files])

    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
