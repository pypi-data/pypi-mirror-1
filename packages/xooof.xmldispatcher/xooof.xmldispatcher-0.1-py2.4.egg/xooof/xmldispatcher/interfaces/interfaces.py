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


from types import UnicodeType

class XMLDispatcherException(RuntimeError):
    """Base XMLDispatcher exception"""

    def __init__(self,descr,source=None,code=None):
        RuntimeError.__init__(self,descr,source,code)
        self.__descr = descr
        self.__code = code
        self.__source = source

    def __str__(self):
        s = "%s [%s] [%s]" % (self.__descr,self.__code,self.__source)
        if type(s) == UnicodeType:
            try:
                return s.encode("utf8")
            except UnicodeError:
                return repr(s)
        else:
            return s

    def getDescr(self):
        return self.__descr

    def getCode(self):
        return self.__code

    def getSource(self):
        return self.__source

    def getType(self):
        # _type must be provided by subclasses
        return self._type

class XMLDispatcherAppException(XMLDispatcherException):
    """Application exception (an exception caused by the server, but due to internal problems)"""
    _type = "AppError"

class XMLDispatcherUserException(XMLDispatcherException):
    """User exception (an exception caused by the client)"""
    _type = "UserError"

class XMLDispatcherSystemException(XMLDispatcherException):
    """Other exception from the app server"""
    _type = "SystemError"

class XMLDispatcherCommException(Exception):
    """Communication (middleware) exception"""
    pass

class IXMLDispatcher:
    """XMLDispatcher low-level interface"""

    def dispatchClassMethodXML(self,className,methodName,xmlRqst,sessionData):
        """Invoke a class method.

           returns (xmlRply,sessionData)"""
        pass

    def dispatchNewInstanceMethodXML(self,className,methodName,xmlRqst,sessionData):
        """Invoke an 'new instance' method (constructor).

           returns (instanceId,sessionData)"""
        pass

    def dispatchInstanceMethodXML(self,className,methodName,instanceId,xmlRqst,sessionData):
        """Invoke an instance method.

           returns (xmlRply,sessionData)"""
        pass

class IXMLDispatcherClient:
    """XMLDispatcher client-level interface.

       This is basically the same as IXMLDispatcher,
       but the sessionData is encapsulated."""

    def dispatchClassMethodXML(self,className,methodName,xmlRqst):
        pass

    def dispatchNewInstanceMethodXML(self,className,methodName,xmlRqst):
        pass

    def dispatchInstanceMethodXML(self,className,methodName,instanceId,xmlRqst):
        pass

    def disconnect(self):
        pass

    def getSessionData(self):
        pass

    def setSessionData(self,sessionData):
        pass
