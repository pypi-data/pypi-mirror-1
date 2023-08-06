# -*- coding: utf-8 -*-
"""
affinitic.verifyinterface

Licensed under the GPL license, see LICENCE.txt for more details.
Copyright by Affinitic sprl

$Id: test_module1.py,v 91ab822f3fb7 2009/12/18 15:56:04 jfroche $
"""
from zope.interface import Interface, Attribute, implements


class IFoo(Interface):
    attribute1 = Attribute('An attribute that you must implement')

    def bla():
        """
        A method you really should implement
        """


class Foo(object):
    implements(IFoo)


import unittest


class FakeTest(unittest.TestCase):

    def testFoo(self):
        self.assertEqual(1 + 1, 2)


def test_suite():
    suite = unittest.TestSuite()
    #XXX remove me before run test
    #suite.addTest(unittest.makeSuite(FakeTest))
    return suite
