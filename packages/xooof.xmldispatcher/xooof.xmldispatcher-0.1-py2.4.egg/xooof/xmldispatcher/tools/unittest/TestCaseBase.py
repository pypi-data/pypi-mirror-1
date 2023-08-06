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


"""Define a TestCaseBase class that helps testing XMLDispatcher servers."""

import difflib, operator, os, re, types, unittest, UserList
from cStringIO import StringIO

from xooof.xmlstruct import xmlstruct
from xooof.xmldispatcher.interfaces.interfaces import XMLDispatcherUserException

try:
    import sliplib
    slip2xml = sliplib.slip2xml
except ImportError:
    def slip2xml(s):
        raise RuntimeError, "sliplib module not available"

import xmlindent

def _htmlEscape(s):
    return s.replace("&","&amp;").replace("<","&lt")

def _isList(o):
    return isinstance(o,UserList.UserList) or type(o) is types.ListType

def _setFieldByNames(struct,splitFieldName,value):
    firstName = splitFieldName[0]
    nextNames = splitFieldName[1:]
    if nextNames:
        # intermediate field
        if _isList(struct):
            for item in struct:
                try:
                    o = getattr(item,firstName)
                except AttributeError:
                    return # field not found: stop now
                else:
                    _setFieldByNames(o,nextNames,value)
        else:
            try:
                o = getattr(struct,firstName)
            except AttributeError:
                return # field not found: stop now
            else:
                _setFieldByNames(o,nextNames,value)
    else:
        # final field
        if not struct is None:
            if _isList(struct):
                for item in struct:
                    setattr(item,firstName,value)
            else:
                setattr(struct,firstName,value)

def _setFieldByName(struct,fullFieldName,value):
    """Set the value of a named struct field.

    The field name must have the following form: x.y.z...

    """
    _setFieldByNames(struct,fullFieldName.split("."),value)

def _indentStruct(struct):
    """Convert a IXMLStruct to an indented XML string."""
    ios = StringIO()
    struct.xsToSAX(xmlindent.XMLIndentGenerator(ios))
    return ios.getvalue()

def _matchString(expectedString,expectedStringIsRegExp,lifeString):
    if not expectedStringIsRegExp:
        return expectedString == lifeString
    else:
        return re.match(expectedString,lifeString) is not None

class StructEqualFailureException(unittest.TestCase.failureException):
    """Base class for all StructEqualFailure exceptions."""

    def toHtml(self,htmlStream):
        """Write exception details as html."""
        pass

class StructEqualFailureExceptionMismatch(StructEqualFailureException):
    """FailureException that indicates a failed struct comparison.

    It holds the expected struct and the life struct, as indented
    strings, suitable for a diff-like display. The toHtml method
    prints a readable diff of the expected and actual structs.

    """

    def __init__(self,expectedStructIndented,lifeStructIndented):
        self.__expectedStructIndented = expectedStructIndented
        self.__lifeStructIndented = lifeStructIndented

    def __str__(self):
        return "struct does not match expected result"

    def toHtml(self,htmlStream):
        expected = self.__expectedStructIndented.split("\n")
        life = self.__lifeStructIndented.split("\n")
        htmlStream.write("<pre>")
        htmlStream.write("-: expected\n")
        htmlStream.write("+: actual\n")
        for line in difflib.ndiff(expected,life):
            htmlStream.write(_htmlEscape(line))
            htmlStream.write("\n")
        htmlStream.write("</pre>")

class StructEqualFailureExceptionExpectedNotFound(StructEqualFailureException):
    """FailureException that indicates that the expected struct was not found.

    It holds the name of the (missing) expected struct file, and
    the indented actual struct, and the exception obtained when
    trying to open the file. The toHtml method prints the actual
    result, in a form suitable for copy/paste, so the user will
    be able to use it as a template to create the expected result
    file.
    """

    def __init__(self,expectedStructFileName,lifeStructIndented,exception):
        self.__expectedStructFileName = expectedStructFileName
        self.__lifeStructIndented = lifeStructIndented
        self.__exception = exception

    def __str__(self):
        return "expected struct file not found: %s (%s)" % \
               (self.__expectedStructFileName,
                self.__exception)

    def toHtml(self,htmlStream):
        htmlStream.write("actual result\n")
        htmlStream.write("<pre>")
        htmlStream.write(_htmlEscape(self.__lifeStructIndented))
        htmlStream.write("\n")
        htmlStream.write("</pre>")

class TestCaseBase(unittest.TestCase):
    """Subclass of unittest.TestCase to help testing XMLDispatcher servers."""

    def getBaseStructDir(self):
        raise RuntimeError, "must be implemented by subclass"

    def getStructFactory(self):
        raise RuntimeError, "must be implemented by subclass"

    def loadStruct(self,structFileName):
        """Load a struct from a named file.

        The file name is prepended with the baseStructDir configuration
        variable (see the config module in this package).

        If the file name has a '.slip' extension, it is considered
        to be in SLiP (http://www.scottsweeney.com/projects/slip)
        format and converted to XML first, otherwise
        it is assumed to be XML.

        """
        xmlfn = os.path.join(self.getBaseStructDir(),structFileName)
        xmls = open(xmlfn).read()
        if os.path.splitext(xmlfn)[1].upper() == ".SLIP":
            xmls = slip2xml(xmls)
        return xmlstruct.fromXML(self.getStructFactory(),xmls)

    def failUnlessUserException(self,callableObj,
                                     args=(),
                                     expectedCode=None,
                                     expectedText=None,
                                     expectedCodeIsRegExp=0,
                                     expectedTextIsRegExp=0):
        """Test that an XMLDispatcherUserException is raised when callableObj
            is called when the supplied positional arguments. Furthermore, it
            is tested that the user exception has the correct code and
            description text. Optionally, the expected code and texts can
            be regular expressions.
        """
        try:
            apply(callableObj,args)
            self.fail("Method succeeded, but it should have " \
                      "raised a user error")
        except XMLDispatcherUserException, e:
            if expectedCode is not None:
                if not _matchString(expectedCode,
                                    expectedCodeIsRegExp,
                                    e.getCode()):
                    self.fail("Method raised a user exception " \
                              "with an unexpected code:\n" \
                              "expected '%s',\n" \
                              "returned '%s'.\n" \
                              "Descr : '%s'\n" \
                              "Source: %s" % \
                              (expectedCode,e.getCode(),
                               e.getDescr(),e.getSource()))
            if expectedText is not None:
                if not _matchString(expectedText,
                                    expectedTextIsRegExp,
                                    e.getDescr()):
                    self.fail("Method raised a user exception " \
                              "with an unexpected text:\n" \
                              "expected '%s',\n" \
                              "returned '%s'.\n" \
                              "Code  : '%s'\n" \
                              "Source: %s" % \
                              (expectedText,e.getDescr(),
                               e.getCode(),e.getSource()))

    def failUnlessStructEqual(self,expectedStruct,lifeStruct,fieldsToIgnore=[],preprocessFunctions=[]):
        """Test that a struct is equal to an expected struct.

        expectedStruct can be a struct or a string. In the latter case,
        it is interpreted as the name of a file containing a struct to be
        loaded with the loadStruct method. If the file cannot be loaded
        the StructEqualFailureExceptionExpectedNotFound failure exception is
        raised, so the test runner can show usable results.

        fieldsToIgnore is a list of field names (x.y.z...) to ignore. Those
        fields are set to None before comparing expected and actual structs.

        preprocessFunction is a list of callables that receives the
        struct as single argument; it is invoked on each struct to compare
        before actually comparing; this can be used to do some preprocessing
        (e.g. ensuring that lists are in the correct order) to account
        for acceptable changes in results; note that fieldsToIgnore could
        be implemented as preprocessFunction that sets all fields to ignore
        to None.

        If the structs don't match, the StructEqualFailureExceptionMismatch
        failure exception is raised. This is handled by the test runner
        to display a readable 'diff' of the expected and actual results.

        """
        #
        # prepare lifeStruct
        #
        if preprocessFunctions or fieldsToIgnore:
            lifeStruct = lifeStruct.xsClone()
        for preprocessFunction in preprocessFunctions:
            preprocessFunction(lifeStruct)
        for fieldName in fieldsToIgnore:
            _setFieldByName(lifeStruct,fieldName,None)
        lifeStructIndented = _indentStruct(lifeStruct)
        #
        # prepare expectedStruct
        #
        if type(expectedStruct) in types.StringTypes:
            # expectedStruct is a string: interpret as a file name and
            # try to load if it exists. If it does not exist,
            # report this as a special error, so the user gets
            # a chance to copy/paste the actual result to the
            # expected result file
            try:
                expectedStruct = self.loadStruct(expectedStruct)
            except (os.error, IOError), e:
                # special error
                raise StructEqualFailureExceptionExpectedNotFound( \
                        expectedStruct,lifeStructIndented,e)
        if preprocessFunctions or fieldsToIgnore:
            expectedStruct = expectedStruct.xsClone()
        for preprocessFunction in preprocessFunctions:
            preprocessFunction(expectedStruct)
        for fieldName in fieldsToIgnore:
            _setFieldByName(expectedStruct,fieldName,None)
        expectedStructIndented = _indentStruct(expectedStruct)
        #
        # compare
        #
        if expectedStructIndented != lifeStructIndented:
            raise StructEqualFailureExceptionMismatch( \
                    expectedStructIndented,lifeStructIndented)
