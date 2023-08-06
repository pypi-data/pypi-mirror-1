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


from xooof.xmldispatcher.interfaces.interfaces import *
from xooof.xmlstruct.xmlstruct import XMLStructError

def validateRqst(rqst,baseClass,canBeNull=0,mustBeValidated=1):
    if rqst is None:
        if not canBeNull:
            raise XMLDispatcherUserException("Missing rqst",
                                             code="XDE_VAL_RQST_MISSING")
    else:
        if not isinstance(rqst,baseClass):
            raise XMLDispatcherUserException("Unexpected rqst type " \
                                             "(got %s, expecting %s)" % \
                                             (type(rqst),baseClass),
                                             code="XDE_VAL_RQST_INV_TYPE")
        if mustBeValidated:
            try:
                rqst.xsValidate("rqst")
            except XMLStructError, e:
                raise XMLDispatcherUserException(str(e),
                                                 code="XDE_VAL_RQST_INV")

def validateRply(rply,baseClass,canBeNull=0,mustBeValidated=1):
    if rply is None:
        if not canBeNull:
            raise XMLDispatcherAppException("Missing rply",
                                             code="XDE_VAL_RPLY_MISSING")
    else:
        if not isinstance(rply,baseClass):
            raise XMLDispatcherAppException("Unexpected rply type " \
                                            "(got %s, expecting %s)" % \
                                            (type(rply),baseClass),
                                            code="XDE_VAL_RPLY_INV_TYPE")
        if mustBeValidated:
            try:
                rply.xsValidate("rply")
            except XMLStructError, e:
                raise XMLDispatcherAppException(str(e),
                                                code="XDE_VAL_RPLY_INV")
