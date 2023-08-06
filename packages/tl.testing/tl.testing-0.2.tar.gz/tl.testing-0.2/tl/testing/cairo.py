# Copyright (c) 2009 Thomas Lotze
# See also LICENSE.txt

from zope.testing import doctest
import manuel
import manuel.doctest
import manuel.footnote
import manuel.testing
import os
import os.path
import re
import sys
import unittest

cairo = manuel.absolute_import('cairo')


class Test(object):

    finder = re.compile(
        r'^\s*\.\. figure:: (?P<src>\S+)$$\s+``(?P<expression>.+)``$',
        re.MULTILINE)

    def __init__(self, document, region):
        self.document = document
        self.region = region
        self.expression = region.start_match.group('expression')
        self.src = region.start_match.group('src')

    def evaluate(self, globs):
        try:
            result = eval(self.expression, globs)
        except:
            return 'Exception raised:\n%s' % doctest._indent(
                doctest._exception_traceback(sys.exc_info()))

        if not isinstance(result, cairo.Surface):
            return 'Expected a cairo surface\nGot:\n    %s\n' % result

        base = os.path.dirname(self.document.location)
        if os.path.isabs(self.src):
            path = self.src
        else:
            path = os.path.join(base, *self.src.split('/'))
        expected = cairo.ImageSurface.create_from_png(path)

        if result.get_data() != expected.get_data():
            return 'Image differs from expectation: %s\n' % self.src


class Result(object):

    def __init__(self, test, error):
        self.test = test
        self.error = error
        self.document = test.document
        self.region = test.region

    def format(self):
        if self.error:
            return ('File "%s", line %s, in %s:\n'
                    'Failed example:\n    %s\n%s' %
                    (self.document.location, self.region.lineno,
                     os.path.basename(self.document.location),
                     self.test.expression, self.error))


class Document(manuel.Document):

    def evaluate_with(self, m, globs):
        globs = manuel.GlobWrapper(globs)
        for region in self:
            for evaluater in manuel.sort_handlers(m.evaluaters):
                evaluater(region, self, globs)


class Manuel(manuel.Manuel):

    def __init__(self, Test, Result):
        self.Test = Test
        self.Result = Result
        super(Manuel, self).__init__(parsers=[self.parse],
                                     evaluaters=[self.evaluate],
                                     formatters=[self.format])
        self.extend(manuel.footnote.Manuel())

    def parse(self, document):
        for region in document.find_regions(self.Test.finder):
            if not region.parsed:
                document.replace_region(region, self.Test(document, region))

    def evaluate(self, region, document, globs):
        if region.evaluated:
            return
        test = region.parsed
        if isinstance(test, self.Test):
            region.evaluated = self.Result(test, test.evaluate(globs))

    def format(self, document):
        for region in document:
            result = region.evaluated
            if isinstance(result, self.Result):
                region.formatted = result.format()


def DocFileSuite(path, module_relative=True, package=None,
                 setUp=None, tearDown=None, globs=None,
                 optionflags=0, checker=None, encoding=None,
                 manuel_object=None):
    m = manuel.doctest.Manuel(optionflags=optionflags, checker=checker)
    m.extend(manuel_object or Manuel(Test, Result))

    if module_relative:
        calling_module = doctest._normalize_module(package)
        path = doctest._module_relative_path(calling_module, path)

    document = Document(open(path).read().decode(encoding or 'ascii'),
                        location=path)

    return unittest.TestSuite([
        manuel.testing.TestCase(m, document,
                                setUp=setUp, tearDown=tearDown, globs=globs)
        ])
