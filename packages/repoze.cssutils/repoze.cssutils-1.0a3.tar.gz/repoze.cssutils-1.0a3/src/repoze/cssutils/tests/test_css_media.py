"""Test css media
"""

import sys
import os
import glob

from repoze.cssutils.common.testrunner import TestSuite, FunctionTestCase, TestProgram
from repoze.cssutils.css import CSSParser, CSSParseError


class TestCSSMediaFiles(TestSuite):
    def generateTests(self):
        rootPath = os.path.dirname(__file__)
        cssFilenames = glob.glob(os.path.join(rootPath, 'media', '*.css'))
        self.getCSSFileTests(cssFilenames)
        self.getSingleParserCSSFileTests(cssFilenames)

    def _generateTestCallback(self, name):
        return lambda:self._testCSSFile(name)

    def getCSSFileTests(self, cssFilenames):
        for cssfilename in cssFilenames:
            testfn = FunctionTestCase(self._generateTestCallback(cssfilename),
                    description='CSSFile with standalone parser for \'%s\''%str(cssfilename))
            self.addTest(testfn)
    
    def _generateSharedTestCallback(self, name, parser):
        return lambda:self._testCSSFileWithParser(name, parser)

    def getSingleParserCSSFileTests(self, cssFilenames):
        parser = CSSParser()
        for cssfilename in cssFilenames:
            testfn = FunctionTestCase(self._generateSharedTestCallback(cssfilename, parser),
                    description='CSSFile with shared parser for \'%s\''%str(cssfilename))
            self.addTest(testfn)

    def _testCSSFile(self, cssfilename):
        parser = CSSParser()
        self._testCSSFileWithParser(cssfilename, parser)

    def _testCSSFileWithParser(self, cssfilename, parser):
        cssfile = open(cssfilename, 'r')
        try:
            try: 
                stylesheet = parser.parseFile(cssfile)
            except CSSParseError, err:
                assert False, 'CSSParser failed to parse \'%s\':: %s' % (cssfilename, err)
        finally:
            cssfile.close()


if __name__=='__main__':
    TestProgram()
