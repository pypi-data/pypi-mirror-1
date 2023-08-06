# -*- coding: utf-8 -*-
"""
affinitic.verifyinterface

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl

$Id: test_docs.py,v 91ab822f3fb7 2009/12/18 15:56:04 jfroche $
"""
from os.path import join
import unittest
import zc.buildout.testing

from zope.testing import doctest, renormalizing

optionflags = (doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE |
               doctest.REPORT_ONLY_FIRST_FAILURE)


def setUp(test):
    zc.buildout.testing.buildoutSetUp(test)
    zc.buildout.testing.install_develop('zc.recipe.testrunner', test)
    zc.buildout.testing.install_develop('zc.recipe.egg', test)
    zc.buildout.testing.install_develop('zope.testing', test)
    zc.buildout.testing.install_develop('zope.interface', test)
    zc.buildout.testing.install_develop('zope.exceptions', test)
    zc.buildout.testing.install_develop('affinitic.verifyinterface', test)


def test_suite():
    #XXX remove me before run test
    return unittest.TestSuite()
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
