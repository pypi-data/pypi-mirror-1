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

class State:

    def __init__(self,name):
        self.name = name or str(id(self))
        self.transitions = {}
        self.isMacroState = 0

    def addTransition(self,event,nextState=None,action=None):
        self.transitions[event] = (nextState, action)

class NState(State):

    def __init__(self):
        State.__init__(self,"nihil")

class MState(State):

    def __init__(self,name = None):
        State.__init__(self,name)
        self.states = {}
        self.isMacroState = 1

    def _addState(self,state):
        self.states[state.name] = state
        return state

    def addState(self,name):
        return self._addState(State(name))

    def addMState(self):
        return self._addState(MState())

    def _flatten(self,fsm,parentTransitions):
        for state in self.states.values():
            transitions = parentTransitions.copy()
            transitions.update(state.transitions)
            if not state.isMacroState:
                fsm[state.name] = transitions
            else:
                state._flatten(fsm,transitions)

    def flatten(self):
        map = {}
        self._flatten(map,{})
        return FlatFSM(map)

class FSM(MState):

    def __init__(self):
        MState.__init__(self)

    def addNState(self):
        return self._addState(NState())

class FlatFSM:

    def __init__(self,map):
        self.__map = map

    def doAction(self,xdo,event,*args):
        """Execute the action on the given object (xdo) for the given event

        The state machine advances and the action method is called.
        """
        state = xdo.getState() or "nihil"
        try:
            transitions = self.__map[state]
        except KeyError:
            raise XMLDispatcherAppException("Unexpected state %s" % state)
        try:
            nextState,action = transitions[event]
        except KeyError:
            raise XMLDispatcherUserException("Event %s is not allowed " \
                                             "in state %s" % \
                                             (event,state),
                                             code="XDE_FSM_EVENT_NOT_ALLOWED")
        if nextState and nextState != state:
            xdo._setState(nextState)
        if action:
            actionMethod = getattr(xdo,action)
            return actionMethod(*args)

    def getActionsForEvent(self,event):
        """Return the list of possible actions for a given event"""
        actions = {}
        for transitions in self.__map.values():
            if transitions.has_key(event):
                nextState,action = transitions[event]
                if action:
                    actions[action] = None
        return actions.keys()

    def getEventsForState(self,state):
        """Return the list of possibles event for a given state"""
        if self.__map.has_key(state):
            return self.__map[state].keys()
        else:
            return []

    def getStatesForEvent(self,event):
        """Return the list of states for a given event"""
        states = []
        for state, transitions in self.__map.items():
            if event in transitions.keys():
                states.append(state)
        return states

    def getStatesForEvents(self,events):
        """Return the list of states for a list of events"""
        _states = []
        for event in events:
            _states.extend(self.getStatesForEvent(event))
        states = []
        for st in _states:
            if st not in states:
                states.append(st)
        return states

    def getInvalidStatesForEvent(self,event):
        """Return the list of invalidate states for a given event"""
        states = []
        for state, transitions in self.__map.items():
            if event not in transitions.keys():
                states.append(state)
        return states

def _test():
    fsm = FSM()
    ns = fsm.addNState()
    ns.addTransition("create","created",None)
    ms = fsm.addMState()
    ms.addTransition("load",None,None)
    ms.addTransition("destroy","nihil",None)
    s = ms.addState("active")
    s.addTransition("deactivate","inactive",None)
    s.addTransition("touch",None,None)
    s = ms.addState("inactive")
    s.addTransition("activate","active",None)
    s.addTransition("touch",None,None)
    s.addTransition("load","active",None)
    print fsm.flatten().getEventsForState("active")
    print fsm.flatten().getStatesForEvent("touch")
    print fsm.flatten().getInvalidStatesForEvent("activate")

if __name__ == '__main__':
    _test()
