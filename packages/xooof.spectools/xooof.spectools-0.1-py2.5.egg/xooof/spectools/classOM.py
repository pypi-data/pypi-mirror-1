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
from commonOM import Descr
from interfaceOM import Event
from interfaceOM import Reply

class Klass:
    def __init__(self):
        self.specFile = None
        self.name = None
        self.descr = []
        self.defaultinterface = None
        self.classmethods = []
        self.fsm = None
        self.classNs = None
        self.doc = []
        if 1:
            # all classes have an implicit getClassInfo method
            e = Event()
            e.name = "getClassInfo"
            e.visibility = "public"
            e.descr = [Descr()]
            e.descr[0].language = "en"
            e.descr[0].description = "Obtain information about the class"
            e.rply = Reply()
            e.rply.className = ("http://xmlcatalog/catalog/spectools/class/classinfo","MClass")
            e.rply.list = 1
            e.rply.optional = 0
            e.rply.validated = 1
            self.classmethods.append(e)

    def __repr__(self):
        return "Klass instance name='%s'" % self.name[1]

    def validate(self):
        """TODO
           - validate name of class [A-Za-z][A-Za-z0-9]*
           - in methods : rqst and rply exists and are valid
           - fsm => consitency of fsm
        """
        raise RuntimeError("not implemented")

    def getAllEvents(self):
        r = self.classmethods
        if self.defaultinterface:
            r = r + self.defaultinterface.getAllEvents()
        return r
