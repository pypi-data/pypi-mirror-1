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

import structnsOM
from commonOM import Descr

#dictionnary of structnsFiles : {SystemID : Ns}
structNsFiles = {}
#directionnary of Ns : {namespace : Ns}
structNamespaces = {}

class NotStructnsException(Exception):
    def __init__(self,filename = "<unknown>"):
        self.filename = filename
    def __repr__(self):
        return "%s is not a structns instance" % self.filename
    def __str__(self):
        return self.__repr__()

def _loadStructns(stream):
    structns = structnsOM.Structns()
    is_first_elem = True
    for event, elem in etree.iterparse(stream, events=("start","end")):
        name = elem.tag
        if event == "start":
            if is_first_elem and name != "structns":
                raise NotStructnsException()
            else:
                is_first_elem = False
        else:
            if name == "descr":
                descr = Descr()
                descr.language = elem.attrib.get("{http://www.w3.org/XML/1998/namespace}lang", None)
                descr.description = elem.text
                structns.descr.append(descr)
            elif name == "ns":
                ns = structnsOM.Ns()
                ns.type = elem.attrib['type']
                ns.package = elem.text or None
                ns.manifest = elem.attrib.get("manifest",None)
                structns.ns[ns.type] = ns
    return structns

def loadStructns(filename):
    path = os.path.normcase(os.path.abspath(filename))
    try:
        return structNsFiles[path]
    except KeyError:
        if os.path.exists(path):
            stream = open(path, "r")
            try :
                s = _loadStructns(path)
                structNsFiles[path] = s
                if s.ns.has_key("xml"):
                    structNamespaces[s.ns["xml"]] = s
                else:
                    structNamespaces[None] = s
                return s
            finally:
                stream.close()
        else:
            s = structnsOM.Structns()
            structNsFiles[path] = s
            structNamespaces[None] = s
            return s

if __name__=="__main__":
    f = "structns.xml"
    s = loadStructns(f)
    for ns in s.ns.values():
        print ns
    print s.descr[0]
