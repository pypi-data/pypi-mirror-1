# Copyright (c) 2008 Thomas Lotze
# See also LICENSE.txt

import os
import os.path
import unittest
from zope.testing import doctest

import tl.testing.fs
import tl.testing.script


flags = (doctest.ELLIPSIS |
         doctest.INTERPRET_FOOTNOTES |
         doctest.NORMALIZE_WHITESPACE |
         doctest.REPORT_NDIFF)


def teardown(test):
    tl.testing.fs.teardown_sandboxes()
    tl.testing.script.teardown_scripts()


def test_suite():
    return unittest.TestSuite([
        doctest.DocFileSuite(filename,
                             package="tl.testing",
                             optionflags=flags,
                             setUp=tl.testing.fs.setup_sandboxes,
                             tearDown=teardown,
                             )
        for filename in sorted(os.listdir(os.path.dirname(__file__)))
        if filename.endswith(".txt")
        ])
