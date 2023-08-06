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
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at
# your option) any later version.
#
# XOo°f is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
# for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
#-##########################################################################-#
import os

from lxml import etree

from fsmOM import FSM
from commonOM import Descr

class NotFsmException(Exception):
    def __init__(self,filename = "<unknown>"):
        filename = filename
    def __repr__(self):
        return "%s is not a fsm instance" % self.filename
    def __str__(self):
        return __repr__()

class NoNStateException(Exception):
    def __init__(self,filename = "<unknown>"):
        filename = filename
    def __repr__(self):
        return "%s has no NState defined as first child of fsm element" % self.filename
    def __str__(self):
        return __repr__()

# TODO doc
def loadFSM(filename):
    path = os.path.normcase(os.path.abspath(filename))
    if not os.path.exists(path):
        raise NotFsmException(filename = filename)
    classDir = os.path.dirname(path)
    fsm = FSM()
    fsm.classSpecFile = filename
    firstElem = 1
    inFsm = False
    curState = None
    data = ""
    container = fsm
    parentContainerStack = []
    for event, elem in etree.iterparse(path, events=("start","end"), attribute_defaults=True):
        name = elem.tag
        if event == 'start':
            if name == "fsm":
                inFsm = True
            if inFsm and name != "fsm":
                if firstElem:
                    if name == "nstate":
                        firstElem = 0
                        curState = container.addNState(elem.attrib["name"])
                    else:
                        raise NoNStateException(fsm.classSpecFile)
                elif name == "mstate":
                    parentContainerStack.append(container)
                    curState = container.addMState()
                    container = curState
                elif name == "state":
                    curState = container.addState(elem.attrib["name"])
                elif name == "transition":
                    curState.addTransition(elem.attrib["event"],
                            elem.attrib.get("nextstate",None),
                            elem.attrib.get("impl",None))
        elif event == "end":
            if inFsm:
                if name == "descr":
                    descr = Descr()
                    descr.language = elem.attrib.get("{http://www.w3.org/XML/1998/namespace}lang", None)
                    descr.description = elem.text
                    curState.descr.append(descr)
                if name == "mstate":
                    container = parentContainerStack.pop()
    return fsm
