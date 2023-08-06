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
import os, types
from sets import Set

import structOM
from structOM import Struct
from structOM import Field
from classOM import Klass
from interfaceOM import Interface
from interfaceOM import Event
from interfaceOM import Request
from interfaceOM import Reply
from fsmOM import FSM
from fsmOM import State
from fsmOM import NState
from fsmOM import MState
import classOM
import class2OM
import struct2OM
import structns2OM
import interface2OM

def _getStructNamespace(p):
    # TODO urljoin
    s = structns2OM.loadStructns(os.path.join(p,"structns.xml"))
    if s.ns.has_key("xml"):
        return s.ns["xml"].package
    else:
        return None

class Specs:
    def __init__(self,dirNames = []):
        self.__structs = {}
        self.__classes = {}
        self.__interfaces = {}
        self.__dirs = {}
        if type(dirNames) in types.StringTypes:
            dirNames = [dirNames]
        self.addDirectory(os.path.join(os.path.dirname(__file__),"classinfo"))
        for dirName in dirNames:
            self.addDirectory(dirName)

    def addDirectory(self,dirName):
        namespace = _getStructNamespace(dirName)
        if not self.__dirs.has_key(namespace):
            self.__dirs[namespace] = []
        self.__dirs[namespace].append(dirName)
        for file in filter(lambda f: os.path.splitext(f)[1] == ".xml",os.listdir(dirName)):
            try:
                struct = struct2OM.loadStruct(os.path.join(dirName,file))
                #print "***",struct
                self.__structs[struct.className] = struct

            except struct2OM.NotStructException:
                try:
                    klass = class2OM.loadClass(os.path.join(dirName,file))
                    # TODO obtain class namespace from classns
                    #print "***",klass
                    self.__classes[klass.name] = klass
                except class2OM.NotClassException:
                    try:
                        interface = interface2OM.loadInterface(os.path.join(dirName,file))
                        self.__interfaces[interface.name] = interface
                    except interface2OM.NotInterfaceException:
                        pass

    def getAllStructNames(self):
        return self.__structs.keys()

    def getAllStructs(self,namespace=-1):
        if namespace == -1:
            return self.__structs.values()
        else:
            allStructs = []
            for key, value in self.__structs.items():
                if key[0] == namespace:
                    allStructs.append(value)
            return allStructs

    def getStruct(self,(namespace,structname)):
        return self.__structs[(namespace,structname)]

    def getAllClassNames(self):
        return self.__classes.keys()

    def getAllClasses(self):
        return self.__classes.values()

    def getAllInterfaces(self):
        return self.__interfaces.values()

    def getInterface(self, name, marker=None):
        return self.__interfaces.get(name, marker)

    def getClass(self,(namespace,classname)):
        return self.__classes[(namespace,classname)]

    def _addDependentStructs(self,set,struct,
            includeSubClasses=1,includeSubClassesOfFields=1):
        if not struct.className in set:
            set.add(struct.className)
            if struct.baseClass:
                self._addDependentStructs(set,self.getStruct(struct.baseClass),
                        0,includeSubClassesOfFields)
            for gfield in struct.gfields:
                if gfield.className[1] != "ANYSTRUCT":
                    self._addDependentStructs(set,
                            self.getStruct(gfield.className),
                            includeSubClassesOfFields,includeSubClassesOfFields)
            for glfield in struct.glfields:
                if glfield.className[1] != "ANYSTRUCT":
                    self._addDependentStructs(set,
                            self.getStruct(glfield.className),
                            includeSubClassesOfFields,includeSubClassesOfFields)
            # TODO this way of detecting subclasses is really heavy!
            if includeSubClasses:
                for s in self.getAllStructs():
                    if s.baseClass == struct.className:
                        self._addDependentStructs(set,s,
                                includeSubClasses,includeSubClassesOfFields)

    def getParentStructsFromStruct(self, struct, set=None):
        """ Return a set of names of parents structs"""
        if set is None:
            set = Set()
        childClasses = self.getDependentStructsFromStruct(struct,includeSubClasses=0,
                includeSubClassesOfFields=0)
        allClasses = self.getDependentStructsFromStruct(struct,includeSubClasses=1,
                includeSubClassesOfFields=0)
        parentClasses = allClasses.difference(childClasses)
        for parentClasse in parentClasses:
            if parentClasse not in set:
                set.add(parentClasse)
        return set

    def getDependentStructsFromStruct(self,struct,set=None,
            includeSubClasses=1,includeSubClassesOfFields=1):
        """ Return a set of names of dependents structs """
        if set is None:
            set = Set()
        self._addDependentStructs(set,struct,
                includeSubClasses,includeSubClassesOfFields)
        return set

    def getDependentStructsFromEvent(self,event,set=None,
            includeSubClasses=1,includeSubClassesOfFields=1):
        """ Return a set of names of structs required for a method  """
        if set is None:
            set = Set()
        if event.rqst:
            self._addDependentStructs(set,self.getStruct(event.rqst.className),
                    includeSubClasses,includeSubClassesOfFields)
        if event.rply:
            self._addDependentStructs(set,self.getStruct(event.rply.className),
                    includeSubClasses,includeSubClassesOfFields)
        return set

    def getDependentStructsFromClass(self,klass,methodNames=None,set=None,
            includeSubClasses=1,includeSubClassesOfFields=1):
        """ Return a set of names of structs required for a class """
        if set is None:
            set = Set()
        for event in klass.classmethods:
            if not methodNames or event.name in methodNames:
                self.getDependentStructsFromEvent(event,set,
                        includeSubClasses,includeSubClassesOfFields)
        if klass.defaultinterface:
            for event in klass.defaultinterface.methods:
                if not methodNames or event.name in methodNames:
                    self.getDependentStructsFromEvent(event,set,
                            includeSubClasses,includeSubClassesOfFields)
            # TODO: extended interfaces
        return set
