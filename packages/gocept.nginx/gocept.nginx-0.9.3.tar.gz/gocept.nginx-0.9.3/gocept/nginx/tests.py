# Copyright (c) 2008 gocept gmbh & co. kg
# See also LICENSE.txt

import unittest

import zope.testing.doctest

import zc.buildout.testing


flags = zope.testing.doctest.ELLIPSIS

#zope.testing.doctest.NORMALIZE_WHITESPACE |


def setUp(test):
    zc.buildout.testing.buildoutSetUp(test)
    zc.buildout.testing.install_develop("gocept.nginx", test)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(zope.testing.doctest.DocFileSuite(
        "README.txt",
        setUp=setUp,
        tearDown=zc.buildout.testing.buildoutTearDown,
        package="gocept.nginx",
        optionflags=flags))
    return suite
