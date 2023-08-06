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

import warnings

from types import TupleType

from xooof.xmldispatcher.interfaces.interfaces import *
from xooof.xmldispatcher.tools.marshallers import StructMarshaller
from xooof.xmldispatcher import classinfo as classInfoStructFactory
from xooof.xmlstruct import xmlstruct

# TBC: _XXXMethodProxies could be replaced by lambda functions?

class _ClassMethodProxy:

    def __init__(self,xdcli,className,methodName):
        self.__xdcli = xdcli
        self.__className = className
        self.__methodName = methodName

    def __call__(self,rqst=None):
        return self.__xdcli.dispatchClassMethod( \
                 self.__className,self.__methodName,rqst)

class _NewInstanceMethodProxy:

    def __init__(self,xdcli,className,methodName):
        self.__xdcli = xdcli
        self.__className = className
        self.__methodName = methodName

    def __call__(self,rqst=None):
        instanceId = self.__xdcli.dispatchNewInstanceMethod( \
                       self.__className,self.__methodName,rqst)
        return _InstanceProxy(self.__xdcli,
                              self.__xdcli.getClassInfo(self.__className),
                              instanceId)

class _InstanceMethodProxy:

    def __init__(self,xdcli,className,methodName,instanceId):
        self.__xdcli = xdcli
        self.__className = className
        self.__methodName = methodName
        self.__instanceId = instanceId

    def __call__(self,rqst=None):
        return self.__xdcli.dispatchInstanceMethod( \
                 self.__className,self.__methodName,self.__instanceId,rqst)

class _ClassProxy:

    def __init__(self,xdcli,classInfo):
        self.__xdcli = xdcli
        self.__classInfo = classInfo
        for cm in classInfo.classmethods:
            setattr(self,cm.name,
                    _ClassMethodProxy(
                      self.__xdcli,classInfo.name,cm.name))
        for im in classInfo.instancemethods:
            if im.special == "constructor":
                setattr(self,im.name,
                        _NewInstanceMethodProxy(
                          self.__xdcli,classInfo.name,im.name))

    def getClassName(self):
        return self.__classInfo.name

    def getClassInfo(self):
        return self.__classInfo

class _InstanceProxy:

    def __init__(self,xdcli,classInfo,instanceId):
        self.__xdcli = xdcli
        self.__instanceId = instanceId
        self.__classInfo = classInfo
        for cm in classInfo.classmethods:
            setattr(self,cm.name,
                    _ClassMethodProxy(
                      self.__xdcli,classInfo.name,cm.name))
        for im in classInfo.instancemethods:
            if im.special == "constructor":
                setattr(self,im.name,
                        _NewInstanceMethodProxy(
                          self.__xdcli,classInfo.name,im.name))
            else:
                setattr(self,im.name,
                        _InstanceMethodProxy(
                          self.__xdcli,classInfo.name,im.name,instanceId))

    def getInstanceId(self):
        return self.__instanceId

    def getClassName(self):
        return self.__classInfo.name

class XMLDispatcherClient(IXMLDispatcherClient):

    def __init__(self,xd,marshaller):
        """Constructor

           - xd must implement IXMLDispatcher
             (it encapsulates the middleware-specific stuff)
           - marshaller must implement
             xooof.xmldispatcher.tools.marshallers.IXMLDispatcherMarshaller
             (it encapsulates the actual format for xmlRqst and xmlRply)"""
        self.__xd = xd
        self.__marshaller = marshaller
        self.__sessionData = ""
        self.__classInfoCache = {}

    # Very-high-level-experimental-not-optimized (TBC) interface

    def getClassInfo(self,className):
        try:
            return self.__classInfoCache[className]
        except KeyError:
            cixml = self.dispatchClassMethodXML(className,"getClassInfo")
            try:
                ci = self.__marshaller.unmarshall(cixml)
            except Exception, e:
                # this is for backward compatibility
                warnings.warn("marshaller could not unmarshall getClassInfo " \
                              "result; trying with the raw struct factory: " + \
                              str(e))
                ci = xmlstruct.fromXML(classInfoStructFactory,cixml)
            self.__classInfoCache[className] = ci
            return ci

    def getClass(self,className):
        # TBC: cache class proxies?
        return _ClassProxy(self,self.getClassInfo(className))

    def getInstance(self,className,instanceId):
        # TBC: cache instance proxies templates and set the
        #      instanceId on a shallow copy?
        #      Measure before optimizing!!!
        return _InstanceProxy(self,self.getClassInfo(className),instanceId)

    # High-level interface (marshalled requests and replies)

    def dispatchClassMethod(self,className,methodName,rqst=None):
        xmlRqst = self.__marshaller.marshall(rqst)
        xmlRply = self.dispatchClassMethodXML(className,methodName,xmlRqst)
        return self.__marshaller.unmarshall(xmlRply)

    def dispatchNewInstanceMethod(self,className,methodName,rqst=None):
        xmlRqst = self.__marshaller.marshall(rqst)
        return self.__marshaller.unmarshallId(self.dispatchNewInstanceMethodXML(className,methodName,xmlRqst))

    def dispatchInstanceMethod(self,className,methodName,instanceId,rqst=None):
        xmlRqst = self.__marshaller.marshall(rqst)
        xmlRply = self.dispatchInstanceMethodXML(className,methodName,instanceId,xmlRqst)
        return self.__marshaller.unmarshall(xmlRply)

    # IXMLDispatcherClient interface

    def dispatchClassMethodXML(self,className,methodName,xmlRqst=""):
        result = self.__xd.dispatchClassMethodXML(
                className,methodName,xmlRqst,self.__sessionData)

        xmlRply = self._processResult(result)
        return xmlRply

    def dispatchNewInstanceMethodXML(self,className,methodName,xmlRqst=""):
        result = self.__xd.dispatchNewInstanceMethodXML(
                className,methodName,xmlRqst,self.__sessionData)

        instanceId = self._processResult(result)
        return instanceId

    def dispatchInstanceMethodXML(self,className,methodName,instanceId,xmlRqst=""):
        result = self.__xd.dispatchInstanceMethodXML(
                className,methodName,instanceId,xmlRqst,self.__sessionData)

        xmlRply = self._processResult(result)
        return xmlRply

    def disconnect(self):
        self.__xd = None
        self.__classInfoCache = {}

    def getSessionData(self):
        return self.__sessionData

    def setSessionData(self,sessionData):
        self.__sessionData = sessionData

    # private functions
    def _processResult(self, result):

        if type(result) is TupleType:
            if len(result) == 2:
                value,self.__sessionData = result
            elif len(result) == 1:
                value = result[0]
                self._sessionData = None
                return value
            elif len(result) == 0:
                value = None
            else:
                raise RuntimeError, "too many values to unpack"
        else:
            value = result
            self.__sessionData = None

        return value
