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


import re, urllib, urllib2
from types import UnicodeType
import xml.sax
from xml.sax import ContentHandler

from xooof.xmldispatcher.interfaces.interfaces import *
from xooof.xmldispatcher.tools.envelope.constants import *
from xooof.xmldispatcher.tools.marshallers import ErrorMarshaller

class HTTPFORMAdapter(IXMLDispatcher):

    def __init__(self,appName,url,urlopener=None):
        self.__appName = appName
        self.__url = url
        if urlopener is None:
            self.__urlopener = urllib2.build_opener()
        else:
            self.__urlopener = urlopener

    def _dispatch(self,verb,className,methodName,instanceId,xmlRqst,sessionData):
        if type(xmlRqst) is UnicodeType:
            xmlRqst = xmlRqst.encode("utf-8")
        # prepare query
        query = {
          XD_F_APPNAME: self.__appName,
          XD_F_VERB: verb,
          XD_F_CLASSNAME: className,
          XD_F_METHODNAME: methodName,
        }
        if instanceId:
            query[XD_F_INSTANCEID] = instanceId
        if xmlRqst:
            query[XD_F_XMLRQST] = xmlRqst
        if sessionData:
            query[XD_F_SESSIONDATA] = sessionData
        # submit
        try:
            f = self.__urlopener.open(self.__url,urllib.urlencode(query))
        except urllib2.HTTPError, e:
            if e.code != 510:
                # TBC: XMLDispatcherCommException
                raise
            else:
                # 510 is our XMLDispatcher error status
                errorString = e.read()
                e.close()
                ErrorMarshaller.unmarshallExceptionFromXML(errorString)
        else:
            try:
                try:
                    sessionData = f.info()["XMLDispatcher-SessionData"]
                except KeyError:
                    sessionData = ""
                return f.read(),sessionData
            finally:
                f.close()

    # IXMLDispatcher interface

    def dispatchClassMethodXML(self,className,methodName,xmlRqst,sessionData):
        return self._dispatch(XD_VERB_CLASS_METHOD,
                              className,methodName,None,
                              xmlRqst,sessionData)

    def dispatchNewInstanceMethodXML(self,className,methodName,xmlRqst,sessionData):
        return self._dispatch(XD_VERB_NEW_INSTANCE_METHOD,
                              className,methodName,None,
                              xmlRqst,sessionData)

    def dispatchInstanceMethodXML(self,className,methodName,instanceId,xmlRqst,sessionData):
        return self._dispatch(XD_VERB_INSTANCE_METHOD,
                              className,methodName,instanceId,
                              xmlRqst,sessionData)
