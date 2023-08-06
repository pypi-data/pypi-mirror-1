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

#from eltree import ElementTree
from lxml import etree

from structOM import Struct
from structOM import Vfield
from structOM import Vlfield
from structOM import Gfield
from structOM import Glfield
from structOM import Xmlfield
from structOM import Datatype
from structOM import Choice
from structOM import Validation
from structns2OM import loadStructns
from commonOM import Descr

#TODO choices
#TBC what to do with doc element?
#TBC this only works with files and not URLs

class NotStructException(Exception):
    def __init__(self,filename = "<unknown>"):
        self.filename = filename
    def __repr__(self):
        return "%s is not a Struct instance" % self.filename
    def __str__(self):
        return self.__repr__()

def getStructNamespace(structDir,relPath=""):
    # TODO urljoin
    p = os.path.join(structDir,relPath,"structns.xml")
    s = loadStructns(p)
    if s.ns.has_key("xml"):
        return s.ns["xml"].package
    else:
        return None

def loadStruct(filename):
    path = os.path.normcase(os.path.abspath(filename))
    if not os.path.exists(path):
        raise NotStructException(filename = filename)
    is_first_elem = True 
    structDir = os.path.dirname(filename)
    struct = Struct()
    struct.specFile = filename
    curVfield = None
    inVfield = 0
    curVlfield = None
    inVlfield = 0
    curGfield = None
    inGfield = 0
    curGlfield = None
    inGlfield = 0
    curXmlfield = None
    inXmlfield = 0
    data = ""
    curDatatype = None
    curChoice = None
    for event, elem in etree.iterparse(path, events=("start","end"), attribute_defaults=True):
        name = elem.tag
        if event == 'start':
            if is_first_elem and name != "struct":
                raise NotStructException()
            else:
                is_first_elem = False
            if name == "struct":
                struct.structNs = loadStructns(os.path.join(structDir, "structns.xml"))
                struct.className = (getStructNamespace(structDir), elem.attrib['class'])
                if elem.attrib.has_key("baseclass"):
                    struct.baseClass = (getStructNamespace(structDir, elem.attrib['baseclasspath']) , elem.attrib['baseclass'])
            elif name == "vfield":
                curVfield = Vfield()
                struct.vfields.append(curVfield)
                struct.fields.append(curVfield)
                inVfield = 1
                curVfield.name = elem.attrib['name']
                curVfield.mandatory = (elem.attrib['mandatory'] == 'y')
                curVfield.serialize = elem.attrib['serialize']
                curVfield.attrib.update(elem.attrib)
            elif name == "vlfield":
                curVlfield = Vlfield()
                struct.vlfields.append(curVlfield)
                struct.fields.append(curVlfield)
                inVlfield = 1
                curVlfield.name = elem.attrib['name']
                curVlfield.minOccur = int(elem.attrib['minOccur'])
                if elem.attrib.has_key("maxOccur"):
                    curVlfield.maxOccur = int(elem.attrib['maxOccur'])
                curVlfield.attrib.update(elem.attrib)
            elif name == "gfield":
                curGfield = Gfield()
                struct.gfields.append(curGfield)
                struct.fields.append(curGfield)
                inGfield = 1
                curGfield.name = elem.attrib['name']
                curGfield.mandatory = (elem.attrib['mandatory'] == 'y')
                curGfield.className = (getStructNamespace(structDir, elem.attrib['classpath']) , elem.attrib['class'])
                curGfield.attrib.update(elem.attrib)
            elif name == "glfield":
                curGlfield = Glfield()
                struct.glfields.append(curGlfield)
                struct.fields.append(curGlfield)
                inGlfield = 1
                curGlfield.name = elem.attrib['name']
                curGlfield.minOccur = int(elem.attrib['minOccur'])
                curGlfield.className = (getStructNamespace(structDir, elem.attrib['classpath']) , elem.attrib['class'])
                if elem.attrib.has_key("maxOccur"):
                    curGlfield.maxOccur = int(elem.attrib['maxOccur'])
                curGlfield.attrib.update(elem.attrib)
            elif name == "xmlfield":
                curXmlfield = Xmlfield()
                struct.xmlfields.append(curXmlfield)
                struct.fields.append(curXmlfield)
                inXmlfield = 1
                curXmlfield.name = elem.attrib['name']
                curXmlfield.mandatory = (elem.attrib['mandatory'] == 'y')
                curXmlfield.attrib.update(elem.attrib)
            elif name in Datatype.DATATYPES:
                curDatatype = Datatype()
                curDatatype.datatype = name
                curDatatype.attrib.update(elem.attrib)
                if elem.attrib.has_key("maxLen"):
                    curDatatype.maxLen = int(elem.attrib['maxLen'])
                if elem.attrib.has_key("minLen"):
                    curDatatype.minLen = int(elem.attrib['minLen'])
                if elem.attrib.has_key("regexp"):
                    curDatatype.regexp = elem.attrib['regexp']
                if elem.attrib.has_key("maxVal"):
                    curDatatype.maxVal = elem.attrib['maxVal']
                if elem.attrib.has_key("minVal"):
                    curDatatype.minVal = elem.attrib['minVal']
                if elem.attrib.has_key("fractionDigits"):
                    curDatatype.fractionDigits = elem.attrib['fractionDigits']
                if elem.attrib.has_key("name"):
                    # for tcode
                    curDatatype.name = elem.attrib['name']
                if elem.attrib.has_key("encoding"):
                    curDatatype.encoding = elem.attrib['encoding']
                if inVfield:
                    curVfield.datatype = curDatatype
                elif inVlfield:
                    curVlfield.datatype = curDatatype
            elif name == "choice":
                curChoice = Choice()
        elif event == "end":
            if name == "vfield":
                inVfield = 0
            elif name == "vlfield":
                inVlfield = 0
            elif name == "gfield":
                inGfield = 0
            elif name == "glfield":
                inGlfield = 0
            elif name == "xmlfield":
                inXmlfield = 0
            elif name == "descr":
                descr = Descr()
                descr.language = elem.attrib.get("{http://www.w3.org/XML/1998/namespace}lang", None)
                descr.description = elem.text
                if inVfield:
                    curVfield.descr.append(descr)
                elif inVlfield:
                    curVlfield.descr.append(descr)
                elif inGfield:
                    curGfield.descr.append(descr)
                elif inGlfield:
                    curGlfield.descr.append(descr)
                elif inXmlfield:
                    curXmlfield.descr.append(descr)
                else:
                    struct.descr.append(descr)
            elif name == "choice.descr":
                descr = Descr()
                descr.language = elem.attrib.get("{http://www.w3.org/XML/1998/namespace}lang", None)
                descr.description = elem.text
                curChoice.descr.append(descr)
            elif name == "choice.value":
                curChoice.value = elem.text
            elif name == "choice":
                curDatatype.choices.append(curChoice)
            elif name == "default" and inVfield:
                curVfield.default = elem.text
            elif name == "validate":
                validation = Validation()
                validation.language = elem.attrib.get("language",None)
                validation.validation = elem.text
                if inVfield:
                    curVfield.validate.append(validation)
                elif inVlfield:
                    curVlfield.validate.append(validation)
                elif inGfield:
                    curGfield.validate.append(validation)
                elif inGlfield:
                    curGlfield.validate.append(validation)
                elif inXmlfield:
                    curXmlfield.validate.append(validation)
    return struct

if __name__=="__main__":
    #s = loadStruct("F:/Projects/elia/dev/evms/shared/specs/SARPOfftakeExport.xml")
    struct = loadStruct("/home/sagblmi/projects/nexus/src/tabellio.officium/tabellio/officium/models/structs/SPersonSearch.xml")
    print struct
    print struct.descr[0]
    for field in struct.vfields:
        print field
        print field.descr[0]
    for field in struct.vlfields:
        print field
        print field.descr[0]
    for field in struct.gfields:
        print field
        print field.descr[0]
    for field in struct.glfields:
        print field
        print field.descr[0]
