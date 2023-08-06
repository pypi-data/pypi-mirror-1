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

from win32com.client import DispatchEx, CastTo
import pythoncom

from com import COMAdapter

def _CreateObject(progId,machine=None):
    try:
        o = DispatchEx(progId,machine)
        try:
            return CastTo(o,"IXMLDispatcher")
        except:
            warnings.warn("%s@%s does not support the IXMLDispatcher " \
                          "interface, trying with default interface" % \
                          (progId,machine))
            return o
    except pythoncom.com_error, errorData:
        raise RuntimeError, "CreateObject(%s,%s) failed: %s" % \
                            (progId,machine,errorData)

class DCOMAdapter(COMAdapter):

    def __init__(self,appName,hostName=None,componentName="XMLDispatcher"):
        COMAdapter.__init__(self)
        self.__appName = appName
        self.__hostName = hostName
        self.__componentName = componentName

    def _connect(self):
        return _CreateObject( \
                      self.__appName+"."+self.__componentName,
                      self.__hostName)
        #print "ok"
