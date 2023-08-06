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


from xml.sax import ContentHandler

#import logging
#log = logging.getLogger("xooof.xmldispatcher.servers.tools.roles")

class IRoleChecker:

    rcsOneByOne = 1
    rcsAllAtOnce = 2

    def getPreferredStrategy(self):
        raise RuntimeError, "getPreferredStrategy must be implemented by subclass"

    def isUserInOneRole(self,xdCtx,roles):
        raise RuntimeError, "isUserInOneRole must be implemented by subclass"

class IRoleDefs:

    def isAllowedByRole(self,xdCtx,roleChecker,
                        className,methodName,stateName=None):
        """Check that the call is allowed by the role-based security

           Note: roleChecker must implement IRoleChecker.
        """
        raise RuntimeError, "isAllowedByRole must be implemented by subclass"

class SimpleRoleDefs(IRoleDefs):

    def __init__(self):
        self.reset()

    def reset(self):
        self.__applicationRoles = [] # roles
        self.__classRoles = {} # className: [roles]
        self.__methodRoles = {} # (className,methodName): [roles]
        self.__transitionRoles = {} # (className,methodName,stateName): [roles]

    def allowApplication(self,role):
        self.__applicationRoles.append(role)

    def allowClass(self,role,className):
        self.__classRoles.setdefault(className,[]).append(role)

    def allowMethod(self,role,className,methodName):
        self.__methodRoles.setdefault((className,methodName),[]).append(role)

    def allowTransition(self,role,className,methodName,stateName):
        self.__transitionRoles.setdefault((className,methodName,stateName),[]).append(role)

    def isAllowedByRole(self,xdCtx,roleChecker,
                        className,methodName,stateName=None):
        allRoles = []
        rcs = roleChecker.getPreferredStrategy()
        assert(rcs in (IRoleChecker.rcsOneByOne,IRoleChecker.rcsAllAtOnce))
        # application
        roles = self.__applicationRoles
        if rcs == IRoleChecker.rcsOneByOne: # and len(roles):
            if roleChecker.isUserInOneRole(xdCtx,roles):
                return 1
        else:
            allRoles += roles
        # class
        try:
            roles = self.__classRoles[className]
        except KeyError:
            pass
        else:
            if rcs == IRoleChecker.rcsOneByOne: # and len(roles):
                if roleChecker.isUserInOneRole(xdCtx,roles):
                    return 1
            else:
                allRoles += roles
        # method
        try:
            roles = self.__methodRoles[(className,methodName)]
        except KeyError:
            pass
        else:
            if rcs == IRoleChecker.rcsOneByOne: # and len(roles):
                if roleChecker.isUserInOneRole(xdCtx,roles):
                    return 1
            else:
                allRoles += roles
        # transition
        if stateName:
            try:
                roles = self.__transitionRoles[(className,methodName,stateName)]
            except KeyError:
                pass
            else:
                if rcs == IRoleChecker.rcsOneByOne: # and len(roles):
                    if roleChecker.isUserInOneRole(xdCtx,roles):
                        return 1
                else:
                    allRoles += roles
        # all roles at once
        if rcs == IRoleChecker.rcsAllAtOnce and len(allRoles):
            if roleChecker.isUserInOneRole(xdCtx,allRoles):
                return 1
        return 0

class SimpleRoleDefsLoaderSAXHandler(ContentHandler):
    """Populate a SimpleRoleDefs instance from a SAX stream

       Assumes the SAX events are from a valid roles.dtd instance.
    """

    def __init__(self,roleDefs):
        self.roleDefs = roleDefs
        self.__callCtx = []

    def _push(self,callable,args):
        self.__callCtx.insert(0,(callable,args))

    def _pop(self):
        del self.__callCtx[0]

    def _top(self):
        return self.__callCtx[0]

    def startElement(self,name,atts):
        if name == "application":
            args = ()
            self._push(self.roleDefs.allowApplication,args)
        elif name == "class":
            args = self._top()[1]+(str(atts["name"]),)
            self._push(self.roleDefs.allowClass,args)
        elif name == "method":
            args = self._top()[1]+(str(atts["name"]),)
            self._push(self.roleDefs.allowMethod,args)
        elif name == "state":
            args = self._top()[1]+(str(atts["name"]),)
            self._push(self.roleDefs.allowTransition,args)
        elif name == "role-ref":
            callable,args = self._top()
            apply(callable,(str(atts["name"]),)+args)

    def endElement(self,name):
        if name in ("application","class","method","state"):
            self._pop()
