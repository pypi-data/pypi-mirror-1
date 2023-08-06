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

class Struct:
    def __init__(self):
        self.specFile = None
        self.descr = []
        self.doc = []
        self.fields = []
        self.vfields = []
        self.vlfields = []
        self.gfields = []
        self.glfields = []
        self.xmlfields = []
        self.validate = []
        self.className = None
        #baseClass is a tuple of form (namespace,className)
        self.baseClass = None
        self.structNs = None

    def __repr__(self):
        return "Struct instance class='%s',baseClass='%s'" \
               % (self.className,self.baseClass)

    def validateStruct(self):
        """TODO
           - validate name of Struct [A-Za-z][A-Za-z0-9]*
           - exclude all keywords from all programming languages
             (warning only, maybe, because struct2xxx should escape
             keywords)
           - (descr and doc for each language given as parameter ?)
           - if specs is given :
             * gfield exists
             * glfield exists
           - loops in subclasses
        """
        raise RuntimeError("not implemented")

class Field(object):

    VFIELD = 0
    GFIELD = 1
    VLFIELD = 2
    GLFIELD = 3
    XMLFIELD = 4

    def __init__(self):
        self.attrib = {}

class Vfield(Field):

    SERIALIZE_ELEMENT = "element"
    SERIALIZE_ATTRIBUTE = "attribute"
    SERIALIZE_PCDATA = "pcdata"

    fieldType = Field.VFIELD

    def __init__(self):
        super(Vfield, self).__init__()
        self.descr = []
        self.datatype = None
        self.default = None
        self.doc = []
        self.validate = []
        self.name = None
        self.mandatory = 1
        self.serialize = Vfield.SERIALIZE_ELEMENT

    def __repr__(self):
        return "Vfield instance name='%s',mandatory='%s', serialize = '%s',datatype='%s',default='%s'" % \
               (self.name,self.mandatory,self.serialize,self.datatype,self.default)

class Vlfield(Field):

    fieldType = Field.VLFIELD

    def __init__(self):
        super(Vlfield, self).__init__()
        self.descr = []
        self.datatype = None
        self.default = None
        self.doc = []
        self.validate = []
        self.name = None
        self.maxOccur = None
        self.minOccur = None

    def __repr__(self):
        return "Vlfield instance name='%s',datatype='%s',maxOccur='%s',minOccur='%s'" % \
               (self.name,self.datatype,self.maxOccur,self.minOccur)

class Gfield(Field):

    fieldType = Field.GFIELD

    def __init__(self):
        super(Gfield, self).__init__()
        self.descr = []
        self.doc = []
        self.validate = []
        self.name = None
        self.mandatory = 1
        self.className = None

    def __repr__(self):
        return "Gfield instance name='%s',mandatory='%s', class = '%s'" % \
               (self.name,self.mandatory,self.className)

class Glfield(Field):

    fieldType = Field.GLFIELD

    def __init__(self):
        super(Glfield, self).__init__()
        self.descr = []
        self.doc = []
        self.validate = []
        self.name = None
        self.className = None
        self.maxOccur = None
        self.minOccur = None

    def __repr__(self):
        return "Glfield instance name='%s',class='%s',minOccur='%s',maxOccur='%s'" % \
               (self.name,self.className,self.minOccur,self.maxOccur)

class Xmlfield(Field):

    fieldType = Field.XMLFIELD

    def __init__(self):
        super(Xmlfield, self).__init__()
        self.descr = []
        self.doc = []
        self.validate = []
        self.name = None
        self.mandatory = 1

    def __repr__(self):
        return "Gfield instance name='%s',mandatory='%s'" % \
               (self.name,self.mandatory)

class Datatype:
    DATATYPES = ( \
                "tstring", \
                "tint", \
                "tdecimal", \
                "tboolean", \
                "tcode", \
                "tdatetime", \
                "ttime", \
                "tdate", \
                "tbinary", \
                )
    def __init__(self):
        self.datatype = None
        self.maxLen = None
        self.minLen = 1
        self.regexp = None
        self.maxVal = None
        self.minVal = None
        self.fractionDigits = None
        self.name = None # for tcode
        self.encoding = None # for tbinary
        self.choices = []
        self.attrib = {}
    def __repr__(self):
        return "Datatype instance : datatype = '%s'" % self.datatype
    def __str__(self):
        return self.__repr__()

class Choice:
    def __init__(self):
        self.value = None
        self.descr = []
        self.doc = []

class Validation:
    def __init__(self):
        self.language = None
        self.validation = None

class StructValidationException:
    def __init__(self):
        self._list = []
    def appendMsg(self,msg):
        self._list.append(msg)
    def appendException(self,ex):
        self._list += ex._list
    def __repr__(self):
        return self._list.join("\n")
