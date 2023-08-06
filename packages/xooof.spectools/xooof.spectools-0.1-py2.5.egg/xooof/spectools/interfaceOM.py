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

class Interface:
    def __init__(self,name):
        self.name = name
        self.specFile = None
        self.descr = []
        self.doc = []
        self.extends = []
        self.methods = []
        self.interfaceNs = None
    
    def getAllEvents(self):
        r = self.methods 
        for interface in self.extends:
            r = r + interface.getAllEvents()
        return r

    def getAllInterfaces(self):
        r = self.extends
        for interface in self.extends:
            r = r + interface.getAllInterfaces()
        return r

    def getInterfaceForEvent(self,event):
        if event in self.methods:
            return self
        for interface in self.extends:
            itf = interface.getInterfaceForEvent(event)
            if itf is not None:
                return itf
        return None

class Event:
    VISIBILITY_PUBLIC = "public"
    VISIBILITY_PRIVATE = "private"
    SPECIAL_CONSTRUCTOR = "constructor"
    SPECIAL_DESTRUCTOR = "destructor"
    
    def __init__(self):
        self.name = None
        self.visibility = None
        self.special = None
        self.rqst = None
        self.rply = None
        self.descr = []
        self.doc = []
        self.isInstanceMethod = None
    
    def __repr__(self):
        return "Event instance : name='%s',visibility='%s',special='%s'" \
                % (self.name,self.visibility,self.special)

class Request:
    def __init__(self):
        self.className = None
        self.classPath = None
        self.isList = None
        self.isOptional = None
        self.isValidated = None
        self.doc = []
    def __repr__(self):
        return "Request Instance : class='%s'" % (self.className,)

class Reply:
    def __init__(self):
        self.className = None
        self.classPath = None
        self.isList = None
        self.isOptional = None
        self.isValidated = None
        self.doc = []
    def __repr__(self):
        return "Reply Instance : class='%s'" % (self.className,)
