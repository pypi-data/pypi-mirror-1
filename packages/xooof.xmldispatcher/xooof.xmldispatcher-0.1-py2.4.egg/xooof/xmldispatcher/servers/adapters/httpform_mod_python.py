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


import sys

from mod_python import apache, util

from xooof.xmldispatcher.interfaces.interfaces import *
from xooof.xmldispatcher.servers.interfaces import *
from xooof.xmldispatcher.tools.envelope.constants import *
from xooof.xmldispatcher.tools.marshallers import ErrorMarshaller
from xooof.xmldispatcher.servers.basic import xdserver

class ModPythonHttpFormXDRequest(xdserver.Request):

    #__slots__ = [ "apache_req" ]
    pass

class ModPythonHttpFormHandler:
    """ A mod_python handler for XMLDispatcher requests using
    the httpform protocol """

    def __init__(self,handlersHead,requestClass=ModPythonHttpFormXDRequest,errorsWithNs=0):
        self.__handlersHead = handlersHead
        self.__requestClass = requestClass
        self.__errorsWithNs = errorsWithNs

    def handler(self,req):
        try:
            fs = util.FieldStorage(req,keep_blank_values=1)
            try:
                appName = fs[XD_F_APPNAME]
            except KeyError:
                appName = None
            verb = fs[XD_F_VERB]
            className = fs[XD_F_CLASSNAME]
            methodName = fs[XD_F_METHODNAME]
            try:
                instanceId = fs[XD_F_INSTANCEID]
            except KeyError:
                instanceId = None
            try:
                xmlRqst = fs[XD_F_XMLRQST]
            except KeyError:
                xmlRqst = ""
            try:
                sessionData = fs[XD_F_SESSIONDATA]
            except KeyError:
                sessionData = ""

            request = self.__requestClass()
            request.verb = verb
            request.appName = appName
            request.className = className
            request.methodName = methodName
            request.instanceId = instanceId
            request.xmlRqst = xmlRqst
            request.sessionData = sessionData.decode("base64")
            request.apache_req = req
            self.__handlersHead.process(request)
        except:
            # return <error> with 510 status
            req.status = 510
            req.content_type = "text/xml; charset=utf-8"
            req.headers_out["Expires"] = "0"
            req.headers_out["Cache-Control"] = "no-cache"
            req.send_http_header()
            req.write(ErrorMarshaller.marshallExceptionToXML(sys.exc_info(),"utf-8",withNs=self.__errorsWithNs))
            return apache.OK
        else:
            if request.xmlRply.startswith("<"):
                req.content_type = "text/xml; charset=utf-8"
            else:
                # for empty replies and NewInstanceMethod replies
                req.content_type = "text/plain; charset=utf-8"
            req.headers_out["Expires"] = "0"
            req.headers_out["Cache-Control"] = "no-cache"
            if request.sessionData:
                req.headers_out["XMLDispatcher-SessionData"] = \
                    request.sessionData.encode("base64").replace("\n","")
            req.send_http_header()
            req.write(request.xmlRply)
            return apache.OK
