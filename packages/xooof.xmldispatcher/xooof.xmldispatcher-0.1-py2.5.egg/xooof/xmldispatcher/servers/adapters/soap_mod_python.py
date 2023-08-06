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
from cStringIO import StringIO
import xml.sax
from xml.sax.saxutils import LexicalXMLGenerator
from xml.sax.handler import feature_namespaces

from xooof.xmldispatcher.interfaces.interfaces import *
from xooof.xmldispatcher.servers.interfaces import *
from xooof.xmldispatcher.tools.envelope.constants import *
from xooof.xmldispatcher.tools.marshallers import ErrorMarshaller
from xooof.xmldispatcher.servers.basic import xdserver
from xooof.xmldispatcher.tools.envelope.constants import * # for verb constants

NS_SOAP_ENV = "http://schemas.xmlsoap.org/soap/envelope/"

class ModPythonSoapXDRequest(xdserver.Request):

    #__slots__ = [ "apache_req" ]
    pass


class _SoapRequestHandler(xml.sax.handler.ContentHandler):
    def __init__(self):
        self.soapHeaderAtts = None
        self.instanceId = None
        self.className = None
        self.methodName = None
        self.xmlRqst = ""
        self.sessionData = ""
        self.operation = None
        self.operationAtts = None
        self.__inSoapBody = False
        self.__inInstanceId = False
        self.__inOperation = False
        self.__requestHandler = None
        self.__requestName = None
        self.__inRequest = False
        self.__inSessionData = False
        self.__data = ""
        self.__prefixes = {}

    def startDocument(self):
        self.xmlRqst = StringIO()
        self.__requestHandler = LexicalXMLGenerator(self.xmlRqst)

    def endDocument(self):
        pass

    def startPrefixMapping(self, prefix, url):
        self.__prefixes[prefix] = url

    def endPrefixMapping(self, prefix):
        if self.__prefixes.has_key(prefix):
            del self.__prefixes[prefix]

    def startElementNS(self, name, qname, atts):
        if atts == None:
            atts = {}
        if name == (NS_SOAP_ENV, "Envelope"):
            self.soapHeaderAtts = atts
        elif name == (NS_SOAP_ENV, "Body"):
            self.__inSoapBody = True
        elif self.__inSoapBody and \
                not name[1] == "instanceId" and \
                self.operation is None :
            self.__inOperation = True
            self.operation = name[1]
            self.className, self.methodName = name[1].split("-")
            self.operationAtts = atts
        elif self.__inSoapBody and \
                self.__inOperation :
            if name[1] == "sessionData" :
                self.__inSessionData = True
            elif name[1] == "instanceId":
                self.__inInstanceId == True
            else:
                if not self.__inRequest:
                    self.__inRequest = True
                    self.__requestName = name[1]

                if qname.find(":") != -1:
                    prefix = qname.split(":")[0]
                else:
                    prefix = None
                if self.__prefixes.has_key(prefix):
                    self.__requestHandler.startPrefixMapping(prefix, self.__prefixes[prefix])
                    del self.__prefixes[prefix]

                self.__requestHandler.startElementNS(name, qname, atts)

    def endElementNS(self, name, qname):
        if name == (NS_SOAP_ENV, "Body"):
            self.__inOperation = False
        elif self.__inInstanceId:
            self.instanceId = self.__data
            self.__inInstanceId = False
            self.__data = ""
        elif self.__inSessionData:
            self.sessionData = self.__data
            self.__inSessionData = False
            self.__data = ""
        elif self.__inRequest:
            self.__requestHandler.characters(self.__data)
            self.__requestHandler.endElementNS(name, qname)
            self.__data = ""
            if name[1] == self.__requestName:
                self.__inRequest = False
                self.xmlRqst = self.xmlRqst.getvalue()

    def characters(self, content):
        self.__data += content

    def error (self, msg):
        print msg


class _SoapResponseGenerator(LexicalXMLGenerator):
    def __init__(self, out, soapRequestHandler, modPythonSoapXDRequest, encoding="utf-8"):
        LexicalXMLGenerator.__init__(self,out,encoding)
        self.__inputHandler = soapRequestHandler
        self.__request = modPythonSoapXDRequest

    def startDocument(self):
        LexicalXMLGenerator.startDocument(self)
        LexicalXMLGenerator.startPrefixMapping(self,"soap","http://www.w3.org/2003/05/soap-envelope")
        LexicalXMLGenerator.startElementNS(self,("http://www.w3.org/2003/05/soap-envelope","Envelope"),"Envelope",self.__inputHandler.soapHeaderAtts)
        LexicalXMLGenerator.startElement(self,"soap:Body",{})
        LexicalXMLGenerator.startElement(self,"%s-Response"%(self.__inputHandler.operation),self.__inputHandler.operationAtts)

    def startElement(self, name, atts):
        if atts == None:
            atts = {}
        LexicalXMLGenerator.startElement(self,name, atts)

    def characters(self,content):
        LexicalXMLGenerator.characters(self,content)

    def endElement(self,name):
        LexicalXMLGenerator.endElement(self,name)


    def endDocument(self):
        LexicalXMLGenerator.startElement(self,"sessionData",{})
        LexicalXMLGenerator.characters(self,self.__request.sessionData.encode("base64").replace("\n",""))
        LexicalXMLGenerator.endElement(self,"sessionData")
        LexicalXMLGenerator.endElement(self,"%s-Response"%(self.__inputHandler.operation))
        LexicalXMLGenerator.endElement(self,"soap:Body")
        LexicalXMLGenerator.endElement(self,"soap:Envelope")
        LexicalXMLGenerator.endDocument(self)

class _SoapFaultGenerator(LexicalXMLGenerator):
    def __init__(self, out, soapRequestHandler, (exc_type,exc_value,exc_traceback), encoding="utf-8"):
        LexicalXMLGenerator.__init__(self,out,encoding)
        self.__inputHandler = soapRequestHandler
        self.__exc_value = exc_value

    def startDocument(self):
        LexicalXMLGenerator.startDocument(self)
        LexicalXMLGenerator.startElement(self,"soap:Envelope",self.__inputHandler.soapHeaderAtts)
        LexicalXMLGenerator.startElement(self,"soap:Body",{})
        LexicalXMLGenerator.startElement(self,"soap:Fault",{})
        LexicalXMLGenerator.startElement(self,"faultcode",{})
        if isinstance(self.__exc_value, XMLDispatcherUserException):
            LexicalXMLGenerator.characters(self,"soap:Client")
        else:
            LexicalXMLGenerator.characters(self,"soap:Server")
        LexicalXMLGenerator.endElement(self,"faultcode")
        LexicalXMLGenerator.startElement(self,"faultstring",{})
        LexicalXMLGenerator.characters(self,self.__exc_value.getDescr() or "")
        LexicalXMLGenerator.endElement(self,"faultstring")
        LexicalXMLGenerator.startElement(self,"faultactor",{})
        LexicalXMLGenerator.characters(self,self.__exc_value.getSource() or self.__exc_value.getType() or "")
        LexicalXMLGenerator.endElement(self,"faultactor")
        LexicalXMLGenerator.startElement(self,"detail",{})


    def startElement(self, name, atts):
        if atts == None:
            atts = {}
        LexicalXMLGenerator.startElement(self,name, atts)

    def characters(self,content):
        LexicalXMLGenerator.characters(self,content)

    def endElement(self,name):
        LexicalXMLGenerator.endElement(self,name)


    def endDocument(self):
        LexicalXMLGenerator.endElement(self,"detail")
        LexicalXMLGenerator.endElement(self,"soap:Fault")
        LexicalXMLGenerator.endElement(self,"soap:Body")
        LexicalXMLGenerator.endElement(self,"soap:Envelope")
        LexicalXMLGenerator.endDocument(self)


class ModPythonSoapHandler:
    """ A mod_python handler for XMLDispatcher requests using
    the soap protocol """

    def __init__(self,handlersHead,requestClass=ModPythonSoapXDRequest,errorsWithNs=1,classFactoryPackageName="bos"):
        self.__handlersHead = handlersHead
        self.__requestClass = requestClass
        self.__errorsWithNs = errorsWithNs
        self.__cFPN = classFactoryPackageName

    def handler(self,req):
        import sys
        try:
            parser = xml.sax.make_parser([])#["drv_libxml2","xml.sax.drivers2.drv_pyexpat"])
            rqstHandler = _SoapRequestHandler()
            parser.setFeature(feature_namespaces, 1)
            parser.setContentHandler(rqstHandler)
            parser.parse(req)
            request = self.__requestClass()
            if rqstHandler.instanceId:
                request.verb = XD_VERB_INSTANCE_METHOD
            elif rqstHandler.methodName in xdserver.PackageClassFactory.instance(self.__cFPN).getClass(rqstHandler.className)._public_constructors:
                request.verb = XD_VERB_NEW_INSTANCE_METHOD
            else:
                request.verb = XD_VERB_CLASS_METHOD

            request.appName = None
            request.className = rqstHandler.className
            request.methodName = rqstHandler.methodName
            request.instanceId = rqstHandler.instanceId
            request.xmlRqst = rqstHandler.xmlRqst
            request.sessionData = rqstHandler.sessionData.decode("base64")
            request.apache_req = req
            self.__handlersHead.process(request)
        except:
            try:
                import sys, traceback
                exc_type, exc_value, exc_tb = sys.exc_info()
                sys.stderr.write("%s\n%s\n%s\n" % (str(exc_type), str(exc_value), "\n".join(traceback.format_tb(exc_tb))))
                sys.stderr.flush()
                # return <soap:Fault> element
                req.content_type = "text/xml; charset=utf-8"
                req.headers_out["Expires"] = "0"
                req.headers_out["Cache-Control"] = "no-cache"
                req.send_http_header()
                xmlRply = StringIO(ErrorMarshaller.marshallExceptionToXML(sys.exc_info(),"utf-8",withNs=self.__errorsWithNs))
                rplyStream = StringIO()
                rplyHandler = _SoapFaultGenerator(rplyStream,rqstHandler,sys.exc_info())
                parser.setContentHandler(rplyHandler)
                parser.parse(xmlRply)
                req.send_http_header()
                req.write(rplyStream.getvalue())
            except:
                req.status = 510
            return apache.OK
        else:
            req.content_type = "text/xml; charset=utf-8"
            req.headers_out["Expires"] = "0"
            req.headers_out["Cache-Control"] = "no-cache"
            if request.xmlRply.startswith("<"):
                xmlRply = StringIO(request.xmlRply)
            else:
                xmlRply = StringIO("""<?xml version="1.0" encoding="utf-8"?><instanceId>%s</instanceId>""" %request.xmlRply)
            rplyStream = StringIO()
            rplyHandler = _SoapResponseGenerator(rplyStream,rqstHandler,request)
            parser.setContentHandler(rplyHandler)
            parser.parse(xmlRply)
            req.send_http_header()
            req.write(rplyStream.getvalue())
            return apache.OK
