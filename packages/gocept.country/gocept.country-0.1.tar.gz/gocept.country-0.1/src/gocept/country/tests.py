# vim:fileencoding=utf-8
# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id: tests.py 5769 2008-05-20 08:05:02Z sweh $
"""Test harness for gocept.country."""

import doctest
import unittest


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocFileSuite('README.txt',
                                       optionflags=doctest.ELLIPSIS))
    return suite
