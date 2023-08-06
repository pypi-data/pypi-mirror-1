# vim:fileencoding=utf-8
# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id: tests.py 5810 2008-05-21 15:50:45Z sweh $
"""Test harness for gocept.country."""

import os.path

import zope.testing
import zope.app.testing.functional
import unittest

layer = zope.app.testing.functional.ZCMLLayer(
    os.path.join(os.path.dirname(__file__), 'ftesting.zcml'),
    __name__, 'gocept.country Layer', allow_teardown=True)

def test_suite():
    suite = unittest.TestSuite()
    test = zope.app.testing.functional.FunctionalDocFileSuite(
                                   'README.txt',
                                   optionflags=zope.testing.doctest.ELLIPSIS)
    test.layer = layer
    suite.addTest(test)
    return suite
