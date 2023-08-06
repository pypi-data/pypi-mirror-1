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
Deserialization of adv. dupe tables.
""" 

__all__ = ('DeserializerException',
           'HeadlessException',
           'UnsupportedTypeException',
           'InvalidValueException',
           'deserialize',
           'unquote',
           'unescape')

import re
from decimal import Decimal
from advdupe.types import LuaTable, Vector, Angle, Player

re_int = re.compile("^\\-?[0-9]+$")
re_float = re.compile("^\\-?([0-9]+\\.[0-9]+)(?:e([\\+\\-][0-9]+))?$")
re_chunk = re.compile("([A-Z0-9]+)\\{(.*?)\\}")

class DeserializerException(Exception):
    pass

class HeadlessException(DeserializerException):
    """
    Raised when no head could be found.
    """

class UnsupportedTypeException(DeserializerException):
    """
    Raised when a serialized object is not supported.
    """

class InvalidValueException(DeserializerException):
    """
    Raised when a value cannot be coerced to its specified type.
    """

def unescape(s):
    s = s.replace("\x80", "\r\n")
    s = s.replace('\\"', '"')
    s = s.replace("\\\\", "\\")
    return s

def unquote(d):
    if d[0] == '"' and d[-1] == '"':
        return unescape(d[1:-1])
    m = re_float.match(d)
    if m:
        return Decimal(m.group(1)) * (10 ** int(m.group(2)) if m.group(2) != None else 1)
    m = re_int.match(d)
    if m:
        return int(d)
    return unescape(d)
    
def deserialize(data, strings):
    tables = deserialize_tables(data, strings)
    for k in tables:
        if k[0] == "H":
            return tables[k]
    raise HeadlessException("Head table not found when unserializing")
    
def deserialize_tables(data, strings):
    tables = {}
    for id, content in re_chunk.findall(data):
        if id not in tables:
            tables[id] = LuaTable()
        tables[id] = deserialize_table(tables, tables[id], strings, content)
    return tables

def deserialize_table(tables, table, strings, data):
    entries = data.split(";")
    for entry in entries:
        if entry.strip() == "": continue
        if '=' in entry: # This table has keys
            kv = entry.split("=", 1)
            if len(kv) == 1: raise DeserializerException("Invalid key/value definition: %s" % entry)
            table[parse_value(kv[0], tables, strings)] = parse_value(kv[1], tables, strings)
        else:
            table.append(parse_value(entry, tables, strings))
    return table

def parse_value(value, tables, strings):
    t, v = value.split(":", 1)
    try:
        if t == "N":
            return unquote(str(v))
        elif t == "S":
            return unquote(v).replace("\xc2", ";")
        elif t == "Z":
            return strings[unquote(v)]
        elif t == "Y":
            return strings[int(v)]
        elif t == "B":
            return v[0] == "t"
        elif t == "V":
            return Vector(*map(float, v.split(",", 2)))
        elif t == "A":
            return Angle(*map(float, v.split(",", 2)))
        elif t == "P":
            return Player(int(v))
        elif t == "T":
            if v not in tables:
                tables[v] = LuaTable()
            return tables[v]
        else:
            raise UnsupportedTypeException("Unsupported serialized value: %s" % value)
    except ValueError:
        raise InvalidValueException("Value could not be coerced to its type: %s" % value)