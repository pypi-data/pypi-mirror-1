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


class IXMLDispatcherClassFactory:

    def getClass(self,className):
        pass

class IXMLDispatcherState:

    def getState(self):
        """Get the object state."""
        pass

    def _setState(self,state):
        """Set the object state.

        This method should not be called directly."""
        pass

class IXMLDispatcherObject:

    def getInstanceId(self):
        """Get the instance primary key."""
        pass

    def getClassName(self):
        """Get the business class name."""
        pass

    def activate(self,instanceId):
        """Called when an existing instance is activated.

        Activate is called before invoking the instance method,
        the first time the object is loaded during a transaction."""
        pass

    def activateNew(self,instanceId):
        """Called when an new instance is activated.

        Assume a constructor named 'create'. First 'create' is
        called as a class method; it must return the instance id.
        Then activateNew is called on a fresh instance. Then
        'postCreate' is called on the next instance."""
        pass

    def deactivate(self,willRollback):
        """Called at the end of the request."""
        pass

class IXMLDispatcherContext:

    def getSession(self):
        pass

    def setSession(self):
        pass

    def getUserData(self):
        pass

    def setUserData(self):
        pass

    def getClass(self,className):
        pass

    def getInstance(self,className,instanceId):
        pass

    def _getNewInstance(self,className,instanceId):
        pass

    def notifyDestroy(self,className,instanceId):
        pass

    def flushCache(self,willRollback=0):
        pass
