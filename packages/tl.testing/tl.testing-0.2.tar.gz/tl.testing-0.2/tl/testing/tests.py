# Copyright (c) 2008-2009 Thomas Lotze
# See also LICENSE.txt

import os
import os.path
import re
import tempfile
import unittest
import zope.testing.renormalizing
from zope.testing import doctest

import tl.testing.cairo
import tl.testing.fs
import tl.testing.script


flags = (doctest.ELLIPSIS |
         doctest.INTERPRET_FOOTNOTES |
         doctest.NORMALIZE_WHITESPACE |
         doctest.REPORT_NDIFF)

checker = zope.testing.renormalizing.RENormalizing([
    (re.compile(r'Running \S+ tests:\n(  Set up \S+ in \S+ seconds.\n)*',
                  re.MULTILINE), '<SET UP>'),
    (re.compile(r'Tearing down left over layers:\n.*',
                  re.MULTILINE), '<TEAR DOWN>'),
    (re.compile(r'[0-9]+\.[0-9]{3} seconds'), 'N.NNN seconds'),
    (re.compile(r'%s.*%ssample\.txt' % (tempfile.gettempdir(), os.sep)),
                '/test_dir/sample.txt'),
    ])


def teardown(test):
    tl.testing.fs.teardown_sandboxes()
    tl.testing.script.teardown_scripts()


def test_suite():
    return unittest.TestSuite([
        tl.testing.cairo.DocFileSuite(filename,
                                      package='tl.testing',
                                      optionflags=flags,
                                      checker=checker,
                                      setUp=tl.testing.fs.setup_sandboxes,
                                      tearDown=teardown,
                                      )
        for filename in ['../../README.txt', 'cairo.txt']
        ] + [
        doctest.DocFileSuite(filename,
                             package="tl.testing",
                             optionflags=flags,
                             checker=checker,
                             setUp=tl.testing.fs.setup_sandboxes,
                             tearDown=teardown,
                             )
        for filename in sorted(os.listdir(os.path.dirname(__file__)))
        if filename.endswith(".txt")
        ])
