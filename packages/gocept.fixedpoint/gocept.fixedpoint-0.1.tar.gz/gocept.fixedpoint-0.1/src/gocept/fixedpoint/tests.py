# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id: tests.py 5447 2007-11-27 15:25:45Z sweh $

import unittest

from zope.testing import doctest


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocFileSuite("fixedpoint.txt",
                                       optionflags=doctest.ELLIPSIS))
    return suite
