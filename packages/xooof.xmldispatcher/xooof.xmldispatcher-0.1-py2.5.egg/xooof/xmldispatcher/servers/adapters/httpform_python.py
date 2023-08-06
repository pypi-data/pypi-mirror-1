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

import BaseHTTPServer, urlparse, cgi

from xooof.xmldispatcher.interfaces.interfaces import *
from xooof.xmldispatcher.servers.interfaces import *
from xooof.xmldispatcher.tools.envelope.constants import *
from xooof.xmldispatcher.tools.marshallers import ErrorMarshaller
from xooof.xmldispatcher.servers.basic import xdserver

class PythonHttpFormXDRequest(xdserver.Request):
    pass

class PythonHttpFormHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    """ A Subclass of BaseHTTPRequestHandler to handle XMLDispatcher
    requests using the httpform protocol """

    def __init__(self,errorsWithNs=0):
        BaseHTTPServer.BaseHTTPRequestHandler.__init__(self)
        self.__errorsWithNs = errorsWithNs

    def getHandlersHead(self,appName):
        raise RuntimeError("getHandlersHead must be overwritten")

    def makeRequest(self):
        return PythonHttpFormXDRequest()

    def dispatch(self,appName,verb,className,methodName,instanceId,
            xmlRqst,sessionData):
        request = self.makeRequest()
        request.verb = verb
        request.appName = appName
        request.className = className
        request.methodName = methodName
        request.instanceId = instanceId
        request.xmlRqst = xmlRqst
        request.sessionData = sessionData
        self.getHandlersHead(appName).process(request)
        return (request.xmlRply,request.sessionData)

    def do_GET(self):
        # prepare an environment, because we are going
        # to use cgi.FieldStorage to parse the request
        environ = {}
        environ["REQUEST_METHOD"] = "GET"
        environ["CONTENT_TYPE"] = "application/x-www-form-urlencoded"
        environ["QUERY_STRING"] = urlparse.urlsplit(self.path)[4]
        self._do_work(environ)

    def do_POST(self):
        # prepare an environment, because we are going
        # to use cgi.FieldStorage to parse the request
        environ = {}
        environ["REQUEST_METHOD"] = "POST"
        if "content-type" in self.headers:
            environ["CONTENT_TYPE"] = self.headers["content-type"]
        if "content-length" in self.headers:
            environ["CONTENT_LENGTH"] = self.headers["content-length"]
        self._do_work(environ)

    def _do_work(self,environ):
        try:
            fs = cgi.FieldStorage(fp=self.rfile,
                                  environ=environ,keep_blank_values=1,
                                  strict_parsing=1)
            try:
                appName = fs[XD_F_APPNAME].value
            except KeyError:
                appName = None
            verb = fs[XD_F_VERB]
            className = fs[XD_F_CLASSNAME].value
            methodName = fs[XD_F_METHODNAME].value
            try:
                instanceId = fs[XD_F_INSTANCEID].value
            except KeyError:
                instanceId = None
            try:
                xmlRqst = fs[XD_F_XMLRQST].value
            except KeyError:
                xmlRqst = ""
            try:
                sessionData = fs[XD_F_SESSIONDATA].value
            except KeyError:
                sessionData = ""

            xmlRply,sessionData = self.dispatch(
                    verb,appName,className,methodName,instanceId,
                    xmlRqst,sessionData)
        except:
            # return <error> with 510 status
            self.send_response(510)
            self.send_header("Content-Type","text/xml; charset=utf-8")
            self.send_header("Expires","0")
            self.send_header("Cache-Control","no-cache")
            self.end_headers()
            self.wfile.write(ErrorMarshaller.marshallExceptionToXML(sys.exc_info(),"utf-8",withNs=self.__errorsWithNs))
        else:
            self.send_response(200)
            if xmlRply.startswith("<"):
                self.send_header("Content-Type","text/xml; charset=utf-8")
            else:
                # for empty replies and NewInstanceMethod replies
                self.send_header("Content-Type","text/plain; charset=utf-8")
            self.send_header("Expires","0")
            self.send_header("Cache-Control","no-cache")
            if sessionData:
                self.send_header["XMLDispatcher-SessionData"] = \
                    sessionData
            self.end_headers()
            self.wfile.write(xmlRply)

if __name__ == "__main__":
    # a test and usage demonstration
    from xooof.xmldispatcher.servers.basic.xdhandlers import NullHandler
    class MyHttpHandler(PythonHttpFormHandler):
        head = NullHandler()
        def getHandlersHead(self,appName):
            return self.head
    httpd = BaseHTTPServer.HTTPServer(('', 8000), MyHttpHandler)
    httpd.serve_forever()
