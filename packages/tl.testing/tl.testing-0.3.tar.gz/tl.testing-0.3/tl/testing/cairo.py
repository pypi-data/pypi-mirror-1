# Copyright (c) 2009 Thomas Lotze
# See also LICENSE.txt

try:
    from zope.testing import doctest
except ImportError:
    import doctest
import manuel
import manuel.doctest
import manuel.footnote
import manuel.testing
import os
import os.path
import re
import sys

cairo = manuel.absolute_import('cairo')

FORMATS = dict((getattr(cairo, attr), 'cairo.'+attr)
               for attr in dir(cairo)
               if 'FORMAT' in attr)


class Test(object):
    """A graphical test that compares a cairo surface with an expected image.

    A test instance represents a test run on one region of a doc-test file.
    The region is identified as being a ReST figure with a caption that is a
    literal expression. The test is characterised by that expression and the
    path to the referenced image.

    The example's Python expression is evaluated in the context of the test
    case's global variables. It is expected to be a cairo Surface. The
    expected graphical content is loaded from the referenced file, which must
    be a PNG image.

    Failures:
        'Exception raised: <traceback>'
            The expression raised an exception when evaluated.
        'Expected a cairo surface, Got: <expression value>'
            The expression's value is not a cairo Surface instance.
        'Image differs from expectation: <path to image>'
            The graphical content of the cairo Surface could be computed but
            does not meer the test's expectation.

    Errors:
        'Could not load expectation: <path to image>'
            The referenced image is not a readable PNG file.

    If the expression could be evaluated to a cairo Surface and the test
    failed or raised an error later, the CAIRO_TEST_RESULTS environment
    variable is consulted. If set, is taken to be the path to an existing
    directory and the surface's content is written to a file in that
    directory. The file name is computed from the path to the expected image.

    """

    finder = re.compile(
        r'^\s*\.\. figure:: (?P<src>\S+)$$\s+``(?P<expression>.+)``$',
        re.MULTILINE)

    def __init__(self, document, region):
        self.document = document
        self.region = region
        self.expression = region.start_match.group('expression')
        self.src = region.start_match.group('src')

    def evaluate(self, globs):
        """Compute the cairo surface under test and compare it with the image.

        Returns the failure message or None if the test passed.

        """
        try:
            result = eval(self.expression, globs)
        except:
            return 'Exception raised:\n%s' % doctest._indent(
                doctest._exception_traceback(sys.exc_info()))

        if not isinstance(result, cairo.ImageSurface):
            return 'Expected a cairo.ImageSurface\nGot:\n    %s\n' % result

        base = os.path.dirname(self.document.location)
        path = os.path.join(base, *self.src.split('/'))

        try:
            expected = cairo.ImageSurface.create_from_png(path)
        except Exception:
            raise Exception('Could not load expectation: %s\n' % self.src
                            + self.store_result(result))

        result_format = result.get_format()
        expected_format = expected.get_format()
        if result_format != expected_format:
            return ('ImageSurface format differs from expectation:\n'
                    'Expected: %s\nGot:      %s\n' %
                    (FORMATS[expected_format], FORMATS[result_format]))

        if self.src.endswith('rgb24.png'):
            result.write_to_png('/tmp/result24.png')
            expected.write_to_png('/tmp/expected24.png')

        raw_result = result
        if result_format == cairo.FORMAT_RGB24:
            # The buffer has undefined bits, producing false mismatches.
            result = copy_to_ARGB32(result)
            expected = copy_to_ARGB32(expected)

        if self.src.endswith('rgb24.png'):
            result.write_to_png('/tmp/result32.png')
            expected.write_to_png('/tmp/expected32.png')

        if result.get_data() != expected.get_data():
            return ('Image differs from expectation: %s\n' % self.src
                    + self.store_result(raw_result))

    def store_result(self, result):
        """Write the surface's content to a file on failure or error.

        Returns a line of output pointing to the file, or '' if no target
        directory is specified by the environment.

        """
        path = os.environ.get('CAIRO_TEST_RESULTS')
        if not path:
            return ''

        path = os.path.join(path, self.src.replace('/', '-'))
        try:
            result.write_to_png(path)
        except Exception:
            return '(could not write result to %s)\n' % path
        else:
            return '(see %s)\n' % path


def copy_to_ARGB32(surface):
    copy = cairo.ImageSurface(
        cairo.FORMAT_ARGB32, surface.get_width(), surface.get_height())
    ctx = cairo.Context(copy)
    ctx.set_source_surface(surface)
    ctx.paint()
    return copy


class Result(object):
    """The result of a test for a cairo Surface's graphical content.

    A test result is characterised by the failure message, which is an empty
    string if the test passed.

    """

    def __init__(self, test, error):
        self.test = test
        self.error = error
        self.document = test.document
        self.region = test.region

    def format(self):
        """Return a formatted failure message if the test failed.

        """
        if self.error:
            return ('File "%s", line %s, in %s:\n'
                    'Failed example:\n    %s\n%s' %
                    (self.document.location, self.region.lineno,
                     os.path.basename(self.document.location),
                     self.test.expression, self.error))


class Manuel(manuel.Manuel):
    """Manuel test runner that exercises Test and Result implementations.

    """

    def __init__(self, Test, Result):
        self.Test = Test
        self.Result = Result
        super(Manuel, self).__init__(parsers=[self.parse],
                                     evaluaters=[self.evaluate],
                                     formatters=[self.format])

    def parse(self, document):
        """Create Test instances for matching regions of a document.

        """
        for region in document.find_regions(self.Test.finder):
            if not region.parsed:
                document.claim_region(region)
                region.parsed = self.Test(document, region)

    def evaluate(self, region, document, globs):
        """Evaluate the region's Test, if any, in the context of globs.

        """
        if region.evaluated:
            return
        test = region.parsed
        if isinstance(test, self.Test):
            region.evaluated = self.Result(test, test.evaluate(globs))

    def format(self, document):
        """Format Results obtained for matching regions of a document.

        """
        for region in document:
            result = region.evaluated
            if isinstance(result, self.Result):
                region.formatted = result.format()


def DocFileSuite(*paths, **options):
    """Return a TestSuite that runs doc-test files with graphical tests.

    Parameters that are the same as for Python's standard doctest.TestSuite:
    module_relative, package, setUp, tearDown, globs, optionflags, checker

    manuel: optional manuel.Manuel instance with additional behaviour

    """
    package = options.pop('package', None)
    relative = options.pop('module_relative', True)
    abs_paths = []
    for path in paths:
        if relative and not os.path.isabs(path):
            calling_module = doctest._normalize_module(package)
            abs_paths.append(
                doctest._module_relative_path(calling_module, path))
        else:
            abs_paths.append(os.path.abspath(path))

    m = (manuel.doctest.Manuel(optionflags=options.pop('optionflags', 0),
                               checker=options.pop('checker', None))
         + manuel.footnote.Manuel()
         + Manuel(Test, Result))
    if 'manuel' in options:
        m += options.pop('manuel')

    return manuel.testing.TestSuite(m, *abs_paths, **options)
