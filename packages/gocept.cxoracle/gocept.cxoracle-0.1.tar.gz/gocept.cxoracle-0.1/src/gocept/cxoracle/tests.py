# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt

import unittest

import zope.testing.doctest

import zc.buildout.testing


flags = (zope.testing.doctest.NORMALIZE_WHITESPACE |
         zope.testing.doctest.ELLIPSIS)


def setUp(test):
    zc.buildout.testing.buildoutSetUp(test)
    zc.buildout.testing.install_develop("gocept.cxoracle", test)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zope.testing.doctest.DocFileSuite(
        "README.txt",
        setUp=setUp,
        tearDown=zc.buildout.testing.buildoutTearDown,
        package="gocept.cxoracle",
        optionflags=flags))
    return suite
