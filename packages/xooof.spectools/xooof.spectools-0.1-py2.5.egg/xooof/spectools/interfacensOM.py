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


class Interfacens:
    def __init__(self):
        #dictionary of the form { type : Ns}
        self.ns = {}
        self.descr = []

    def __repr__(self):
        return "Interfacens instance ns = %s" % self.ns

    def getValue(self,key):
        val = self.ns.get(key,None)
        if val is not None:
            return val.package
class Ns:
    def __init__(self):
        #dictionary of the form { type : (#PCDATA,)}
        self.type = {}
        self.package = None

    def __repr__(self):
        return "Ns instance type='%s',package='%s'" % (self.type,self.package)
