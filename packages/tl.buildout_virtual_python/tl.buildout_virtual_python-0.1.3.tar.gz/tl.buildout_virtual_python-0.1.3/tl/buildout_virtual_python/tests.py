# Copyright (c) 2008 Thomas Lotze
# See also LICENSE.txt

import os
import os.path
import unittest
from zope.testing import doctest

import zc.buildout.testing
import zc.recipe.egg # import before installing into sample buildout


flags = (doctest.ELLIPSIS |
         doctest.INTERPRET_FOOTNOTES |
         doctest.NORMALIZE_WHITESPACE |
         doctest.REPORT_NDIFF)


def setUp(test):
    zc.buildout.testing.buildoutSetUp(test)
    zc.buildout.testing.install("zc.recipe.egg", test)
    zc.buildout.testing.install_develop("tl.buildout_virtual_python", test)


def test_suite():
    return unittest.TestSuite([
        doctest.DocFileSuite(filename,
                             setUp=setUp,
                             tearDown=zc.buildout.testing.buildoutTearDown,
                             package="tl.buildout_virtual_python",
                             optionflags=flags,
                             )
        for filename in sorted(os.listdir(os.path.dirname(__file__)))
        if filename.endswith(".txt")
        ])
