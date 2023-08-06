# Copyright (c) 2008-2009 Thomas Lotze
# See also LICENSE.txt

import os
import os.path
import manuel.footnote
import pkg_resources
import re
import shutil
import sys
import tempfile
import zope.testing.renormalizing
import zope.testing.testrunner.runner
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
    (re.compile(r'%s.*-test_dir%s' % (tempfile.gettempdir(), os.sep)),
     '/test_dir/'),
    ])


def setup(test):
    tl.testing.fs.setup_sandboxes()


def teardown(test):
    tl.testing.fs.teardown_sandboxes()
    tl.testing.script.teardown_scripts()


def cairo_setup(test):
    test.test_dir = tempfile.mkdtemp(suffix='-test_dir')
    test.original_cwd = os.getcwd()
    os.chdir(test.test_dir)

    for name in ['rgb24.png']:
        shutil.copyfile(
            pkg_resources.resource_filename('tl.testing', 'testimages/'+name),
            os.path.join(test.test_dir, name))

    def write(path, text):
        f = open(path, 'w')
        f.write(text)
        f.close()
        return os.path.abspath(path)

    def run(suite):
        zope.testing.testrunner.runner.Runner(found_suites=[suite]).run()

    test.globs.update(write=write, run=run)

    os.environ.pop('CAIRO_TEST_RESULTS', '')


def cairo_teardown(test):
    os.chdir(test.original_cwd)
    shutil.rmtree(test.test_dir)


def test_suite():
    options = dict(optionflags=flags,
                   checker=checker,
                   setUp=setup,
                   tearDown=teardown,
                   )
    testfiles = set(filename
                    for filename in os.listdir(os.path.dirname(__file__))
                    if filename.endswith('.txt'))
    cairo_testfiles = set(filename for filename in testfiles
                          if filename.startswith('cairo'))

    suite = doctest.DocFileSuite(
        *sorted(testfiles-cairo_testfiles), **options)

    options.update(setUp=cairo_setup, tearDown=cairo_teardown)
    suite.addTest(doctest.DocFileSuite(*sorted(cairo_testfiles), **options))

    options['manuel'] = manuel.footnote.Manuel()
    suite.addTest(tl.testing.cairo.DocFileSuite(
            '../../README.txt', 'cairo.txt', **options))

    return suite
