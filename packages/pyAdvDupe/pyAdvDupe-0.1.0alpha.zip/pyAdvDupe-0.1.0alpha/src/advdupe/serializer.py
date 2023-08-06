#!/usr/bin/env python
#
# pyAdvDupe
# Copyright (C) 2008-2009 sk89q <http://sk89q.therisenrealm.com>
#
# This program is free software: you can redistribute it and/or modify it under 
# the terms of the GNU General Public License as published by the Free
# Software Foundation: either version 2 of the License, or (at your option) 
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more 
# details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# $Id$

"""
Class to serialize adv. dupe data.
""" 

__all__ = ('SerializerException',
           'UnserializableException',
           'serialize',
           'quote',
           'escape')

from cStringIO import StringIO
from decimal import Decimal
from advdupe.types import LuaTable, Vector, Angle, Player

class SerializerException(Exception):
    pass

class UnserializableException(SerializerException):
    """
    Raised when an object can't be serialized.
    """

def escape(s):
    s = s.replace("\\", "\\\\")
    s = s.replace('"', '\\"')
    s = s.replace("\r\n", "\x80")
    return s

def quote(d):
    if isinstance(d, str):
        return '"%s"' % escape(d)
    return "%s" % d

def serialize(table, strings):
    output = StringIO()
    serializer = Serializer(table, strings)
    for k in serializer.tables:
        v = serializer.tables[k]
        if serializer.is_head(table, k):
            output.write("H%s{%s}" % (k, v))
        else:
            output.write("%s{%s}" % (k, v))
    return output.getvalue(), serializer.saved

class IDGenerator:
    def __init__(self):
        self.id = 0
        self.stored = {}
    
    def identify(self, v):
        if id(v) not in self.stored:
            self.id = self.id + 1
            self.stored[id(v)] = self.id
            return str(self.id).zfill(8)
        else:
            return str(self.stored[id(v)]).zfill(8)

class Serializer:
    """
    Helper class to do serialization. Rather than use functions, we are
    using a class to simplify the task of keeping state. It's not much
    a problem when deserializing.
    """
    
    def __init__(self, table, strings):
        self.strings = strings
        self.tables = {}
        self.id_gen = IDGenerator()
        self.saved = 0
        self.serialize_table(table)
    
    def is_head(self, head, key):
        return self.id_gen.identify(head) == key
    
    def serialize_table(self, table):
        id = self.id_gen.identify(table)
        if id in self.tables:
            return id
        
        output = StringIO()
        if len(table) > 0:
            if not isinstance(table, LuaTable):
                table = LuaTable(table)
            if table.is_sequential():
                for key in table:
                    output.write("%s;" % self.serialize_value(table[key]))
            else:
                for key in table:
                    output.write("%s=%s;" % (self.serialize_value(key),
                                             self.serialize_value(table[key])))
        else:
            output.write(";")
        self.tables[id] = output.getvalue()
        
        return id
                    
    def serialize_value(self, value):
        if isinstance(value, str):
            if value in self.strings:
                self.saved = self.saved + 1
                return "Y:%s" % self.strings[value]
            else:
                id = len(self.strings) + 1
                self.strings[value] = id
                return "Y:%s" % self.strings[value]
        elif isinstance(value, bool):
            return "B:t" if value else "B:f"
        elif isinstance(value, Vector):
            return "V:%s,%s,%s" % (value[0], value[1], value[2])
        elif isinstance(value, Angle):
            return "A:%s,%s,%s" % (value[0], value[1], value[2])
        elif isinstance(value, Player):
            return "P:%s" % (value.unique_id)
        elif isinstance(value, dict) or isinstance(value, list):
            return "T:%s" % (self.serialize_table(value))
        elif isinstance(value, Decimal):
            return "N:%s" % str(value)
        elif isinstance(value, int) or isinstance(value, float):
            return "N:%s" % value
        else:
            raise UnserializableException("Object of type %s not unserializable" % type(value))