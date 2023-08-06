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

from commonOM import Descr
from interfaceOM import Event
from interfaceOM import Request
from interfaceOM import Reply
from interfaceOM import Interface
from interfacens2OM import loadInterfacens

from structns2OM import loadStructns
def getStructNamespace(classDir,relPath=""):
    p = os.path.join(classDir,relPath,"structns.xml")
    s = loadStructns(p)
    if s.ns.has_key("xml"):
        return s.ns["xml"].package
    else:
        return None

class NotInterfaceException(Exception):
    def __init__(self,filename = "<unknown>"):
        filename = filename
    def __repr__(self):
        return "%s is not an interface instance" % self.filename
    def __str__(self):
        return __repr__()

def loadInterface(filename):
    path = os.path.normcase(os.path.abspath(filename))
    if not os.path.exists(path):
        raise NotInterfaceException(filename = filename)
    interfaceDir = os.path.dirname(path)
    interface = None
    interfaceFileName = path
    is_first_elem = True
    curElem = None
    curObject = None
    inEvent = 0
    inExtends = 0
    for event, elem in etree.iterparse(path, events=("start","end"), attribute_defaults=True):
        name = elem.tag
        if event == 'start':
            if is_first_elem and name != "interface":
                raise NotInterfaceException(filename=filename)
            else:
                is_first_elem = False
            if name == "interface":
                interface = Interface(elem.attrib['name'])
                curObject = interface
                interface.specFile = interfaceFileName
                nsPath = os.path.join(interfaceDir, "interfacens.xml")
                if os.path.exists(nsPath):
                    interface.interfaceNs = loadInterfacens(nsPath)
            elif name == "event":
                curEvent = Event()
                curObject = curEvent
                inEvent = 1
                curEvent.name = elem.attrib['name']
                curEvent.visibility = elem.attrib['visibility']
                curEvent.isInstanceMethod = True
                if elem.attrib.has_key('special'):
                    curEvent.special = elem.attrib['special']
                interface.methods.append(curEvent)
            elif name == "rqst" or name == "rply":
                o = None
                if name =="rqst":
                    o = Request()
                    curObject = o
                    curEvent.rqst = o
                else:
                    o = Reply()
                    curObject = o
                    curEvent.rply = o
                o.className = (getStructNamespace(interfaceDir,elem.attrib['classpath']) , elem.attrib['class'])
                if elem.attrib['classpath'] is not None:
                    o.classPath = os.path.join(os.path.abspath(interfaceDir),elem.attrib['classpath'])
                o.isList = (elem.attrib['list'] == "y")
                o.isOptional = (elem.attrib['optional'] == "y")
                o.isValidated = (elem.attrib['validated'] == "y")
            elif name == "extends":
                inExtends = 1
                interface.extends.append(loadInterface(os.path.join(interfaceDir,elem.attrib['interfacepath'],elem.attrib['interface']+".xml")))
        elif event == 'end':
            if name == "descr":
                descr = Descr()
                descr.language = elem.attrib.get("{http://www.w3.org/XML/1998/namespace}lang", None)
                descr.description = elem.text
                if inEvent:
                    curEvent.descr.append(descr)
                else:
                    interface.descr.append(descr)
            elif name == "event":
                inEvent = 0
            elif name == "extends":
                inExtends = 0
            elif name == "doc":
                curObject.doc.append(etree.tostring(elem))
    return interface
