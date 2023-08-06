# Copyright (c) 2009 gocept gmbh & co. kg
# See also LICENSE.txt

import unittest
from zope.testing import doctest


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocFileSuite('copyright.txt'))
    return suite
