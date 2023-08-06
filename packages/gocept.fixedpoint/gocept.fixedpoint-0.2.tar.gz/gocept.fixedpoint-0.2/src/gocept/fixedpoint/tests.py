# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id: tests.py 5847 2008-05-26 15:55:23Z sweh $

import unittest

from zope.testing import doctest


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocFileSuite("README.txt",
                                       optionflags=doctest.ELLIPSIS))
    return suite
