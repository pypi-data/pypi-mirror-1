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


import urllib2
from types import UnicodeType
# can I have some elementtree, please?
try:
    from xml.etree import cElementTree as ElementTree # python 2.5
except ImportError:
    try:
        import cElementTree as ElementTree
    except ImportError:
        from elementtree import ElementTree

from xooof.xmldispatcher.interfaces.interfaces import IXMLDispatcher
from xooof.xmldispatcher.tools.envelope.constants import XD_VERB_INSTANCE_METHOD
from xooof.xmldispatcher.tools.envelope.constants import XD_VERB_NEW_INSTANCE_METHOD
from xooof.xmldispatcher.tools.envelope.constants import XD_VERB_CLASS_METHOD


# SOAP 1.1 namespaces
NS_SOAP_ENV = "{http://schemas.xmlsoap.org/soap/envelope/}"
NS_SOAP_ENC = "{http://schemas.xmlsoap.org/soap/encoding/}"
NS_SOAP_ADDR = "{http://schemas.xmlsoap.org/ws/2004/03/addressing/}"
NS_XSI = "{http://www.w3.org/1999/XMLSchema-instance}"
NS_XSD = "{http://www.w3.org/1999/XMLSchema}"


SOAP_ENCODING = "http://schemas.xmlsoap.org/soap/encoding/"

# Namespaces for UsernameToken based authentication
WS_SEC = "http://schemas.xmlsoap.org/ws/2002/07/secext"
NS_WS_SEC = "{" + WS_SEC + "}"
NS_WS_UTIL = "{http://schemas.xmlsoap.org/ws/2002/07/utility}"

class SoapFault(Exception):
    """ SOAP fault exepction
    """

    ##
    # SOAP fault code.

    faultcode = None

    ##
    # SOAP fault description.

    faultstring = None

    ##
    # SOAP fault actor.

    faultactor = None

    ##
    # SOAP fault detail.  This is either None or an Element structure.

    detail = None

    def __init__(self, faultcode, faultstring, faultactor, detail):
        Exception.__init__(self, faultcode, faultstring, faultactor, detail)
        self.faultcode = faultcode
        self.faultstring = faultstring
        self.faultactor = faultactor
        self.detail = detail

def SoapElement(parent, name, typeName=None, text=None):
    # add a typed SOAP element to a request structure
    elem = ElementTree.SubElement(parent, name)
    if typeName:
        if not isinstance(typeName, ElementTree.QName):
            typeName = ElementTree.QName("http://www.w3.org/1999/XMLSchema", typeName)
        elem.set(NS_XSI + "type", typeName)
    elem.text = text
    return elem


class SOAPAdapter(IXMLDispatcher):
    def __init__(self,classNs, url,urlopener=None):
        self.__classNs = classNs
        self.__url = url
        if urlopener is None:
            self.__urlopener = urllib2.build_opener()
        else:
            self.__urlopener = urlopener


    def _dispatch(self,verb,className,methodName,instanceId,xmlRqst,sessionData):
        if type(xmlRqst) is UnicodeType:
            xmlRqst = xmlRqst.encode("utf-8")

        action = self.__classNs + "/%s/%sRequest"%(className, methodName)
        #build soap envelope
        envelope = ElementTree.Element(NS_SOAP_ENV + "Envelope")
        header = ElementTree.Element(NS_SOAP_ENV + 'Header')
        SoapElement(header, NS_SOAP_ADDR + "Action", text=action)
        envelope.append(header)

        body = ElementTree.SubElement(envelope, NS_SOAP_ENV + "Body")
        request = ElementTree.Element("{%s}%s-%s"%(self.__url, className, methodName))
        body.append(request)

        if instanceId:
            SoapElement(request, "instanceId", "string", instanceId)
        if xmlRqst:
            request.append(ElementTree.XML(xmlRqst) )
        if sessionData:
            SoapElement(request, "sessionData", "string", sessionData)
        # submit
        try:
            query = urllib2.Request(self.__url, ElementTree.tostring(envelope))
            query.add_header("Content-type", "text/xml")
            query.add_header("SOAPAction", action)
            response = ElementTree.parse(self.__urlopener.open(query))
        except urllib2.HTTPError, e:
            import ipdb; ipdb.set_trace()
            if e.code == 500:
                # might be a SOAP fault
                raise Exception(e.read())
            raise e

        headers = response.findall(NS_SOAP_ENV + "Header")
        # FIXME: check mustunderstand attribute

        response = response.find(body.tag)[0]

        # fixup any XSI_type attributes
        # FIXME: only do this if envelope uses known soapencoding
        for elem in response.getiterator():
            typeName = elem.get(NS_XSI + "type")
            if typeName:
                elem.set(NS_XSI + "type", namespace_qname(elem, typeName))

        # look for fault descriptors
        if response.tag == NS_SOAP_ENV + "Fault":
            faultcode = response.find("faultcode")
            raise SoapFault(
                faultcode.text,
                response.findtext("faultstring"),
                response.findtext("faultactor"),
                response.findtext("faultdetail")
                )
        else:
            children = response.getchildren()
            instanceId = response.findtext("instanceId")
            if instanceId is not None:
                return instanceId
            if len(children):
                response = ElementTree.tostring(children[0])
            else:
                response = ""

        return response

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

def namespace_parse(source):
    """ Namespace-aware parser.  This parser attaches a namespace attribute
    to all elements.

    @param source Source (a file-like object).
    @return A 2-tuple containing an annotated element tree, and a qname
        resolution helper.  The helper takes an element and a QName, and
        returns an expanded URL/local part string.
    """
    events = ("start", "end", "start-ns", "end-ns")
    ns = []
    context = ElementTree.iterparse(source, events=events)
    for event, elem in context:
        if event == "start-ns":
            ns.append(elem)
        elif event == "end-ns":
            ns.pop()
        elif event == "start":
            elem.set("(xmlns)", tuple(ns))
    return context.root


def namespace_qname(element, qname):
    """ Convert a QName string to an Element-style URL/local part string.
    Note that the parser converts element tags and attribute names
    during parsing; this method should only be used on attribute values
    and text sections.

    @param element An element created by the {@link namespace_parse}
        function.
    @param qname The QName string.
    @return The expanded URL/local part string.
    @throws SyntaxError If the QName prefix is not defined for this
        element.
    """
    prefix, local = qname.split(":")
    for p, url in element.get("(xmlns)"):
        if prefix == p:
            return "{%s}%s" % (url, local)
    raise SyntaxError("unknown namespace prefix (%s)" % prefix)
