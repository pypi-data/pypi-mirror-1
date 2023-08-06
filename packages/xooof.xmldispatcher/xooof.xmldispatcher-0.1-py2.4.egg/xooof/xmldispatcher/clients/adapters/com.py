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


import re

import pythoncom

from xooof.xmldispatcher.interfaces.interfaces import *

def _fix(s):
    return s.replace("\r\n","\n").decode("iso-8859-1")

class COMAdapter(IXMLDispatcher):
    """Abstract base class for adapters to the IXMLDispatcher COM interface"""

    def __init__(self):
        self.__xd = None

    def _connect(self):
        """Return the COM IXMLDispatcher object"""
        raise RuntimeError, "_connect must be implemented by subclasses"

    _code_descr_re = re.compile("(\\S*)::(.*)",re.DOTALL|re.MULTILINE)

    def _splitCodeDescr(self,description):
        mo = self._code_descr_re.match(description)
        if mo is not None:
            #print "*",description
            return mo.groups()
        else:
            return None,description

    def _handleError(self,errorData):
        self.__xd = None # release
        hr,msg,exc,arg = errorData
        if exc is None:
            raise XMLDispatcherSystemException(msg,"",hr)
        else:
            wcode, source, text, helpFile, helpId, scode = exc
            if scode == -2147217183:
                code,descr = self._splitCodeDescr(text)
                raise XMLDispatcherUserException(_fix(descr),_fix(source),code)
            elif scode == -2147220270:
                code,descr = self._splitCodeDescr(text)
                raise XMLDispatcherAppException(_fix(descr),_fix(source),code)
            else:
                # TBC: some information lost here
                # TBC: how to detect XMLDispatcherCommException?
                raise XMLDispatcherSystemException(_fix(text),_fix(source),hex(scode))

    # IXMLDispatcher interface

    def dispatchClassMethodXML(self,className,methodName,xmlRqst,sessionData):
        if self.__xd is None:
            self.__xd = self._connect()
        #print "dispatchClassMethodXML",className,methodName,"...",
        try:
            r = self.__xd.DispatchClassMethodXML( \
                  className,methodName,xmlRqst,sessionData)
            #print "ok"
            return r
        except pythoncom.com_error, errorData:
            #print "error"
            self._handleError(errorData)

    def dispatchNewInstanceMethodXML(self,className,methodName,xmlRqst,sessionData):
        if self.__xd is None:
            self.__xd = self._connect()
        #print "dispatchNewInstanceMethodXML",className,methodName,"...",
        try:
            r = self.__xd.DispatchNewInstanceMethodXML( \
                className,methodName,xmlRqst,sessionData)
            #print "ok"
            return r
        except pythoncom.com_error, errorData:
            #print "error"
            self._handleError(errorData)

    def dispatchInstanceMethodXML(self,className,methodName,instanceId,xmlRqst,sessionData):
        if self.__xd is None:
            self.__xd = self._connect()
        #print "dispatchInstanceMethodXML",className,methodName,instanceId,"...",
        try:
            r = self.__xd.DispatchInstanceMethodXML( \
                  className,methodName,instanceId,xmlRqst,sessionData)
            #print "ok"
            return r
        except pythoncom.com_error, errorData:
            #print "error"
            self._handleError(errorData)
