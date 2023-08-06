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

class State:
    """
    state is used to declare a state of the state-diagram.

    Attributes:
    - name: the name of the state

    Content:
        - descr+: a short description of the state (1 line)
        - doc*: detailed documentation of the state's purpose
        - transition*: the list of transitions that can be executed from this state
    """
    def __init__(self,name):
        self.descr=[]
        self.doc=[]
        self.name = name or str(id(self))
        self.transitions = {}
        self.isMacroState = 0

    def addTransition(self,event,nextState=None,action=None):
        self.transitions[event] = (nextState, action)

class NState(State):
    """
    nstate represents the nihil state, the initial
    state when the object does not yet exist

    Attributes:
        - name: the name of the nihil state, defaults to 'nihil'

    Content:
        - transition*: the list of possible transitions
        - transitions starting from nstate must be
          triggered by constructor events (and vice-versa)
        - transitions ending in nstate must be
          triggered by destructor events (and vice-versa)
    """
    def __init__(self,name="nihil"):
        State.__init__(self,name)

class MState(State):
    """
    mstate is used to declare a macro state.
    A macro state is an abstract state that contains substates
    (other macro states and/or states).
    Transitions declared inside a macro state are available to
    all states defined
    inside this macro state.


    Attributes:

    Content:
        - descr+: a short description of the mstate (1 line)
        - doc*: detailed documentation of the mstate's purpose
        - transition*: list of transitions that can be executed from
          all states defined inside this mstate
        - (mstate|state)+: the sub macro-states and states
    """
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

    def getAllStates(self):
        states = []
        for state in self.states.values():
            if not state.isMacroState:
                states.append(state)
            else:
                states.extend(state.getAllStates())
        return states

        return self.states.values()

    def flatten(self):
        map = {}
        self._flatten(map,{})
        return FlatFSM(map)

class FSM(MState):
    """
    FSM represent a state diagram composed by Meta-States (mstate),
    states (state), and transitions representing the actions done
    when a transition occurs.
    """
    def __init__(self):
        MState.__init__(self)
        self.classSpecFile = None

    def addNState(self,name):
        return self._addState(NState(name))

class FlatFSM:
    def __init__(self,map):
        self.__map = map

    def getActionsForEvent(self,event):
        """Return the list of possible actions for a given event"""
        actions = {}
        for transitions in self.__map.values():
            if transitions.has_key(event):
                nextState,action = transitions[event]
                if action:
                    actions[action] = None
        return actions.keys()

    def getNextStateForEventInState(self,event,state):
        """Return the next state for a given event in a given state"""
        if self.__map.has_key(state):
            nextState, action = self.__map[state][event]
            return nextState
        return None

    def getActionForEventInState(self,event,state):
        """Return the action for a given event in a given state"""
        if self.__map.has_key(state):
            nextState, action = self.__map[state][event]
            return action
        return None

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
