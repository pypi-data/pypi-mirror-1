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

# Jython only adapter

from xooof.xmldispatcher.interfaces.interfaces import *

# java stuff
import org.xooof.xmldispatcher.interfaces.XMLDispatcherException
import org.xooof.xmldispatcher.interfaces.XMLDispatcherUserException
import org.xooof.xmldispatcher.interfaces.XMLDispatcherAppException
import org.xooof.xmldispatcher.interfaces.XMLDispatcherSystemException

class JavaXMLDispatcherClientAdapter(IXMLDispatcher):
    """ A jython adapter for any java XMLDispatcherClient implementation """

    def __init__(self,jxd):
        """ constructor from a Java XMLDispatcherClient instance """
        self.__jxd = jxd

    def _handleError(self,e):
        descr = e.getMessage()
        source = "N/A" # TBC: obtain stack trace from the java exception
        code = e.getCode()
        if isinstance(e,org.xooof.xmldispatcher.interfaces.XMLDispatcherUserException):
            raise XMLDispatcherUserException(descr,source,code)
        elif isinstance(e,org.xooof.xmldispatcher.interfaces.XMLDispatcherAppException):
            raise XMLDispatcherAppException(descr,source,code)
        elif isinstance(e,org.xooof.xmldispatcher.interfaces.XMLDispatcherSystemException):
            raise XMLDispatcherSystemException(descr,source,code)
        else:
            raise RuntimeError("unknown exception from java: "+str(e))

    # IXMLDispatcher interface

    def dispatchClassMethodXML(self,className,methodName,xmlRqst,sessionData):
        self.__jxd.setSessionData(sessionData)
        try:
            xml = self.__jxd.dispatchClassMethodXML(className,methodName,xmlRqst)
            return xml,self.__jxd.getSessionData()
        except org.xooof.xmldispatcher.interfaces.XMLDispatcherException, e:
            self._handleError(e)

    def dispatchNewInstanceMethodXML(self,className,methodName,xmlRqst,sessionData):
        self.__jxd.setSessionData(sessionData)
        try:
            xml = self.__jxd.dispatchNewInstanceMethodXML(className,methodName,xmlRqst)
            return xml,self.__jxd.getSessionData()
        except org.xooof.xmldispatcher.interfaces.XMLDispatcherException, e:
            self._handleError(e)

    def dispatchInstanceMethodXML(self,className,methodName,instanceId,xmlRqst,sessionData):
        self.__jxd.setSessionData(sessionData)
        try:
            xml = self.__jxd.dispatchInstanceMethodXML(className,methodName,instanceId,xmlRqst)
            return xml,self.__jxd.getSessionData()
        except org.xooof.xmldispatcher.interfaces.XMLDispatcherException, e:
            self._handleError(e)
