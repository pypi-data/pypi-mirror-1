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


# the prefix for renamed implementation methods
# (must match $impl-pfx in class2py.xslt)
_impl_pfx = '_'

def _basecheck(base,mname):
    if base.__dict__.has_key(mname):
        return 1
    for basebase in base.__bases__:
        if _basecheck(basebase,mname):
            return 1
    return 0

def _check(clsdict,clsname,bases,mname):
    """Helper to check that the implementation method is present in the user class"""
    if clsdict.has_key(_impl_pfx+mname):
        return
    for base in bases:
        if _basecheck(base,_impl_pfx+mname):
            return
    raise RuntimeError("Xooof method implementation %s is missing in " \
                       "class %s and its base classes" % \
                       (_impl_pfx+mname,clsname))

def _add(clsdict,clsname,mname,mvalue):
    """Helper to add a xooof method to the user class"""
    if clsdict.has_key(mname):
        raise RuntimeError("Xooof method %s would hide user-provided " \
                           "attribute or method in class %s" % \
                           (mname,clsname))
    clsdict[mname] = mvalue

def _getXooofClass(clsdict,clsname):
    if clsdict.has_key('__xooofpackage__'):
        package = clsdict['__xooofpackage__']
        module = __import__(package.__name__+"."+clsname,
                globals(),locals(),[clsname])
        return getattr(module,clsname)
    elif clsdict.has_key('__xooofclass__'):
        return clsdict['__xooofclass__']
    else:
        raise RuntimeError("XooofMetaClass requires a __xooofpackage__ " \
                           "or __xooofclass__ class attribute to be defined")

class XooofMetaClass(type):
    """Metaclass to add xooof-specified behaviour to a user class

    The user class must have a __xooofclass__ attribute
    that specifies the xooof-generated class containing the
    specified behaviour (state machine, validation of request
    and replies). Alternatively, it can have a __xooofpackage__
    attribute referencing the package containing all the
    xooof-generated classes.

    This metaclass adds the xooof-generated behaviour and
    hides the user-provided implementations, to which the
    xooof-generated behaviour will delegate.
    """

    def __new__(cls,clsname,bases,clsdict):
        # TODO: add generated interfaces?
        xooofClass = _getXooofClass(clsdict,clsname)
        xooofClassDict = xooofClass.__dict__
        # fsm
        try:
            fsm = xooofClass._fsm
        except AttributeError:
            fsm = None
        else:
            _add(clsdict,clsname,'_fsm',fsm)
        _add(clsdict,clsname,'_public_class_methods',
                xooofClassDict['_public_class_methods'])
        _add(clsdict,clsname,'_public_constructors',
                xooofClassDict['_public_constructors'])
        _add(clsdict,clsname,'_public_instance_methods',
                xooofClassDict['_public_instance_methods'])
        _add(clsdict,clsname,'getClassInfo',
                xooofClassDict['getClassInfo'])
        # get class info
        ci = xooofClass.getClassInfo()
        # class methods
        for cm in ci.classmethods:
            if cm.name != 'getClassInfo':
                _check(clsdict,clsname,bases,cm.name)
            _add(clsdict,clsname,cm.name,xooofClassDict[cm.name])
        # instance methods and constructors
        for im in ci.instancemethods:
            if im.special == 'constructor':
                _check(clsdict,clsname,bases,im.name)
            if fsm:
                for action in fsm.getActionsForEvent(im.name):
                    assert(action.startswith(_impl_pfx))
                    _check(clsdict,clsname,bases,action[len(_impl_pfx):])
            else:
                if im.special == 'constructor':
                    _check(clsdict,clsname,bases,
                            'post'+im.name[0].upper()+im.name[1:])
                else:
                    _check(clsdict,clsname,bases,im.name)
            _add(clsdict,clsname,im.name,xooofClassDict[im.name])
        # we're done
        return type.__new__(cls,clsname,bases,clsdict)
