# Copyright (c) 2007 Thomas Lotze
# See also LICENSE.txt

"""Test suite for tl.buildout_apache.
"""

import unittest

import zope.testing.doctest

import zc.buildout.testing


flags = (zope.testing.doctest.NORMALIZE_WHITESPACE |
         zope.testing.doctest.ELLIPSIS
         )


def setUp(test):
    zc.buildout.testing.buildoutSetUp(test)
    zc.buildout.testing.install("gocept.download", test)
    zc.buildout.testing.install("gocept.cmmi", test)
    zc.buildout.testing.install_develop("tl.buildout_apache", test)


def test_suite():
    return unittest.TestSuite((
        zope.testing.doctest.DocFileSuite(
        "root.txt",
        setUp=setUp,
        tearDown=zc.buildout.testing.buildoutTearDown,
        package="tl.buildout_apache",
        optionflags=flags,
        ),
        ))


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
