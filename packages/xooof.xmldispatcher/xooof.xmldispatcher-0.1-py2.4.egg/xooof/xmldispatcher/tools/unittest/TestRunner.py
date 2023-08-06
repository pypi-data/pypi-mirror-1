# -*- coding: utf-8 -*-
#-##########################################################################-#
#
# XOo°f - http://www.xooof.org
# A development and XML specification framework for documenting and
# developing the services layer of enterprise business applications.
# From the specifications, it generates WSDL, DocBook, client-side and
# server-side code for Java, C# and Python.
#
# Copyright (C) 2006 Software AG Belgium
#
# This file is part of XOo°f.
#
# XOo°f is free software; you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation; either version 2.1 of the License, or
# (at your option) any later version.
#
# XOo°f is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public
# License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
#-##########################################################################-#


import sys, string, time, unittest, traceback

import TestCaseBase

def _htmlEscape(s):
    return s.replace("&","&amp;").replace("<","&lt")

class _WritelnDecorator:
    """Used to decorate file-like objects with a handy 'writeln' method"""
    def __init__(self,stream):
        self.stream = stream

    def __getattr__(self, attr):
        return getattr(self.stream,attr)

    def writeln(self, *args):
        if args: apply(self.write, args)
        self.write('\n') # text-mode streams translate to \r\n if needed


class _TextAndHtmlTestResult(unittest.TestResult):
    """A test result class that can print formatted to a text stream and an html stream.

    Used by TextAndHtmlTestRunner.
    """
    separator1 = '=' * 70
    separator2 = '-' * 70

    def __init__(self, htmlStream, textStream, descriptions, verbosity):
        unittest.TestResult.__init__(self)
        self.htmlStream = htmlStream
        self.textStream = textStream
        self.showAll = verbosity > 1
        self.dots = verbosity == 1
        self.descriptions = descriptions
        # this is to workaround the fact that TestRunner
        # converts the sys.exc_info to string in errors and failures
        self.myErrors = []
        self.myFailures = []

    def getDescription(self, test):
        if self.descriptions:
            return test.shortDescription() or str(test)
        else:
            return str(test)

    def getHtmlDescription(self, test):
        return "<b>%s</b> [%s]" % (_htmlEscape(self.getDescription(test)),_htmlEscape(str(test)))

    def startTest(self, test):
        unittest.TestResult.startTest(self, test)
        if self.showAll:
            self.textStream.write(self.getDescription(test))
            self.textStream.write(" ... ")

    def addSuccess(self, test):
        unittest.TestResult.addSuccess(self, test)
        # text
        if self.showAll:
            self.textStream.writeln("ok")
        elif self.dots:
            self.textStream.write('.')
        # html
        self.htmlStream.writeln("<tr><td>%s</td><td>OK</td></tr>" % (self.getHtmlDescription(test),))

    def addError(self, test, err):
        unittest.TestResult.addError(self, test, err)
        self.myErrors.append((test,err))
        # text
        if self.showAll:
            self.textStream.writeln("ERROR")
        elif self.dots:
            self.textStream.write('E')
        # html
        self.htmlStream.writeln("<tr><td>%s</td><td><a href='#ERROR%d'>ERROR</a></td></tr>" % (self.getHtmlDescription(test),len(self.errors)))

    def addFailure(self, test, err):
        unittest.TestResult.addFailure(self, test, err)
        self.myFailures.append((test,err))
        # text
        if self.showAll:
            self.textStream.writeln("FAIL")
        elif self.dots:
            self.textStream.write('F')
        # html
        self.htmlStream.writeln("<tr><td>%s</td><td><a href='#FAIL%d'>FAIL</a></td></tr>" % (self.getHtmlDescription(test),len(self.failures)))

    def printTextErrors(self):
        if self.dots or self.showAll:
            self.textStream.writeln()
        self.printTextErrorList('ERROR', self.myErrors)
        self.printTextErrorList('FAIL', self.myFailures)

    def printTextErrorList(self, flavour, errors):
        for test, err in errors:
            self.textStream.writeln(self.separator1)
            self.textStream.writeln("%s: %s" % (flavour,self.getDescription(test)))
            self.textStream.writeln(self.separator2)
            self.textStream.writeln("%s" % string.join(apply(traceback.format_exception, err),''))

    def printHtmlErrors(self):
        self.printHtmlErrorList('ERROR', self.myErrors)
        self.printHtmlErrorList('FAIL', self.myFailures)

    def printHtmlErrorList(self, flavour, errors):
        i = 0
        for test, err in errors:
            i += 1
            self.htmlStream.writeln("<hr><a name='%s%d'/>" % (flavour,i))
            self.htmlStream.writeln("<p>%s</p>" % self.getHtmlDescription(test))
            self.htmlStream.write("<pre>")
            self.htmlStream.writeln(_htmlEscape("%s" % string.join(apply(traceback.format_exception, err),'')))
            self.htmlStream.writeln("</pre>")
            if isinstance(err[1],TestCaseBase.StructEqualFailureException):
                err[1].toHtml(self.htmlStream)


class TextAndHtmlTestRunner:
    """A test runner class that displays results in textual form.

    It prints out the names of tests as they are run, errors as they
    occur, and a summary of the results at the end of the test run.
    """
    def __init__(self, htmlStream, textStream=sys.stderr, descriptions=1, verbosity=1):
        self.htmlStream = _WritelnDecorator(htmlStream)
        self.textStream = _WritelnDecorator(textStream)
        self.descriptions = descriptions
        self.verbosity = verbosity

    def _makeResult(self):
        return _TextAndHtmlTestResult(self.htmlStream, self.textStream, self.descriptions, self.verbosity)

    def run(self, test):
        "Run the given test case or test suite."
        result = self._makeResult()
        startTime = time.time()
        self.htmlStream.writeln("<html><head><title>Test results</title></head><body>")
        self.htmlStream.writeln("<table border='1'>")
        try:
            test(result)
            complete = 1
        except KeyboardInterrupt:
            complete = 0
        self.htmlStream.writeln("</table>")
        stopTime = time.time()
        timeTaken = float(stopTime - startTime)
        run = result.testsRun
        # errors to text result
        result.printTextErrors()
        self.textStream.writeln(result.separator2)
        # text and html summary
        if complete:
            self.textStream.writeln("Ran %d test%s in %.3fs" %
                                (run, run == 1 and "" or "s", timeTaken))
            self.textStream.writeln()
            self.htmlStream.writeln("<p>Ran %d test%s in %.3fs</p>" %
                                (run, run == 1 and "" or "s", timeTaken))
            self.htmlStream.writeln()
        else:
            self.textStream.writeln("Interrupted by user")
            self.textStream.writeln()
            self.htmlStream.writeln("<p>Interrupted by user</p>")
            self.htmlStream.writeln()
        if not result.wasSuccessful():
            self.textStream.write("FAILED (")
            self.htmlStream.write("FAILED (")
            failed, errored = map(len, (result.failures, result.errors))
            if failed:
                self.textStream.write("failures=%d" % failed)
                self.htmlStream.write("failures=%d" % failed)
            if errored:
                if failed: self.textStream.write(", ")
                self.textStream.write("errors=%d" % errored)
                self.htmlStream.write("errors=%d" % errored)
            self.textStream.writeln(")")
            self.htmlStream.writeln(")")
            self.textStream.writeln("")
            self.textStream.writeln("Detailed results are in result.html")
        else:
            self.textStream.writeln("OK")
            self.htmlStream.writeln("OK")
        # errors to html result
        result.printHtmlErrors()
        self.htmlStream.writeln("</body></html>")
        return result

def main(module='__main__',
         defaultTest=None,
         argv=None,
         testRunner=None,
         testLoader=unittest.defaultTestLoader):
    if argv is None:
        argv = sys.argv
    if "-v" in argv:
        verbosity = 2
    elif "-q" in argv:
        verbosity = 0
    else:
        verbosity = 1
    if testRunner is None:
        testRunner = TextAndHtmlTestRunner(open("result.html","w"),verbosity=verbosity)
    unittest.TestProgram(module,defaultTest,argv,testRunner,testLoader)

def _myimport(moduleName):
    module = __import__(moduleName)
    for part in moduleName.split('.')[1:]:
        module = getattr(module, part)
    return module

def loadTestsFromModuleNames(moduleNames,
                             testLoader=unittest.defaultTestLoader):
    test = unittest.TestSuite()
    modules = map(_myimport,moduleNames)
    for module in modules:
        test.addTest(testLoader.loadTestsFromModule(module))
    return test
