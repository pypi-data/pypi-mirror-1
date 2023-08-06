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
Advanced duplicator parser document class.
""" 

__all__ = ('AdvDupeDocument',
           )

from cStringIO import StringIO
from datetime import datetime
import copy
from advdupe.types import Vector, Angle
from advdupe.deserializer import deserialize, unquote, unescape
from advdupe.serializer import serialize, quote, escape

def preferential_sorted(l, order):
    def p_sort(a, b):
        if a in order and b not in order:
            return -1
        elif a not in order and b in order:
            return 1
        elif a in order and b in order:
            return order[a] - order[b]
        else:
            return cmp(a, b)
    return sorted(l, p_sort)

class InvalidDateException(Exception):
    pass

class AdvDupeDocument:
    header_order = [
        "Type", "Creator", "Date", "Description", "Entities",
        "Constraints"
    ]
    header_order = dict(zip(header_order, range(0, len(header_order))))
    extra_header_order = [
        "FileVersion", "AdvDupeVersion", "AdvDupeToolVersion",
        "AdvDupeSharedVersion", "SerialiserVersion", "WireVersion",
        "WireVersion", "Time", "Head", "HoldAngle", "HoldPos",
        "StartPos",
    ]
    extra_header_order = dict(zip(extra_header_order, range(0, len(extra_header_order))))
    
    def __init__(self):
        self.type = "AdvDupe File"
        self.creator = "pyAdvDupe"
        self.save_date = datetime.now()
        self.description = "none"
        self.file_version = "0.84"
        self.version = "1.85"
        self.tool_version = "1.9"
        self.shared_version = "1.72"
        self.serializer_version = "1.4"
        self.wire_version = "1722"
        self.heading = Angle(0, 0, 0)
        self.hold_angle = Angle(0, 0, 0)
        self.hold_pos = Vector(0, 0, 0)
        self.start_pos = Vector(0, 0, 0)
        
        self.header = {}
        self.extra_header = {}
        self.strings = {}
        self.entities = {}
        self.constraints = {}
    
    def get_populated_header(self):
        header = copy.copy(self.header)
        header['Type'] = self.type
        header['Creator'] = quote(self.creator)
        header['Date'] = self.save_date.strftime("%m/%d/%y")
        header['Description'] = quote(self.description)
        header['Entities'] = len(self.entities)
        header['Constraints'] = len(self.constraints)
        return header
    
    def get_populated_extra_header(self):
        extra_header = copy.copy(self.extra_header)
        extra_header['FileVersion'] = self.file_version
        extra_header['AdvDupeVersion'] = self.version
        extra_header['AdvDupeToolVersion'] = self.tool_version
        extra_header['AdvDupeSharedVersion'] = self.shared_version
        extra_header['SerialiserVersion'] = self.serializer_version
        extra_header['WireVersion'] = self.wire_version
        extra_header['Time'] = self.save_date.strftime("%I:%M %p")
        extra_header['Head'] = self.heading.str_elements()
        extra_header['HoldAngle'] = self.hold_angle.str_elements()
        extra_header['HoldPos'] = self.hold_pos.str_elements()
        extra_header['StartPos'] = self.start_pos.str_elements()
        return extra_header
    
    def load(self, path):
        f = open(path, "rb")
        data = f.read()
        f.close()
        self.loads(data)
    
    def loads(self, data):
        input_entities = ""
        input_constraints = ""
        strings = {}
        save_date = None
        save_time = None
        
        lines = data.split("\r\n")
        cur_section = None
        for line in lines:
            if len(line) == 0: continue
            if len(line) >= 3 and line[0] == "[" and line[-1] == "]":
                cur_section = line[1:-1]
            elif cur_section != None:
                kv = line.split(":", 1)
                if cur_section == "Info":
                    if kv[0] == "Type": self.type = kv[1]
                    elif kv[0] == "Creator": self.creator = unquote(kv[1])
                    elif kv[0] == "Date": save_date = kv[1]
                    elif kv[0] == "Description": self.description = unquote(kv[1])
                    else: self.header[kv[0]] = kv[1]
                elif cur_section == "More Information":
                    if kv[0] == "FileVersion": self.file_version = kv[1]
                    elif kv[0] == "AdvDupeVersion": self.version = kv[1]
                    elif kv[0] == "AdvDupeToolVersion": self.tool_version = kv[1]
                    elif kv[0] == "AdvDupeSharedVersion": self.shared_version = kv[1]
                    elif kv[0] == "SerialiserVersion": self.serializer_version = kv[1]
                    elif kv[0] == "WireVersion": self.wire_version = kv[1]
                    elif kv[0] == "Time": save_time = kv[1]
                    elif kv[0] == "Head": self.heading = Angle(*map(float, kv[1].split(",", 2)))
                    elif kv[0] == "HoldAngle": self.hold_angle = Angle(*map(float, kv[1].split(",", 2)))
                    elif kv[0] == "HoldPos": self.hold_pos = Vector(*map(float, kv[1].split(",", 2)))
                    elif kv[0] == "StartPos": self.start_pos = Vector(*map(float, kv[1].split(",", 2)))
                    else: self.extra_header[kv[0]] = kv[1]
                elif cur_section == "Save":
                    if kv[0] == "Entities":
                        input_entities = kv[1]
                    elif kv[0] == "Constraints":
                        input_constraints = kv[1]
                elif cur_section == "Dict":
                    if kv[0] == "Saved":
                        no_save_strs = int(kv[1])
                    else:
                        strings[int(kv[0])] = unescape(kv[1][1:-1])
        
        try:
            self.save_date = datetime.strptime("%s %s" % (save_date, save_time), "%m/%d/%y %I:%M %p")
        except ValueError:
            raise InvalidDateException("Invalid date/time: %s %s" % (save_date, save_time))
        
        self.entities = deserialize(input_entities, strings)
        self.constraints = deserialize(input_constraints, strings)
    
    def dumps(self):
        output = StringIO()
        strings = {}
        saved = 0
        
        # Write header
        output.write("[Info]\r\n")
        header = self.get_populated_header()
        for k in preferential_sorted(header.keys(), self.header_order):
            output.write("%s:%s\r\n" % (k, header[k]))
        
        # Write extra header
        output.write("[More Information]\r\n")
        extra_header = self.get_populated_extra_header()
        for k in preferential_sorted(extra_header.keys(), self.extra_header_order):
            output.write("%s:%s\r\n" % (k, extra_header[k]))
        
        output.write("[Save]\r\n")
        serialized, saved_ = serialize(self.entities, strings)
        saved = saved + saved_
        output.write("Entities:%s\r\n" % serialized)
        serialized, saved_ = serialize(self.constraints, strings)
        saved = saved + saved_
        output.write("Constraints:%s\r\n" % serialized)
        
        output.write("[Dict]\r\n")
        strings_rev = dict((v, k) for k, v in strings.iteritems())
        for k in sorted(strings_rev.keys()):
            output.write("%s:%s\r\n" % (k, quote(strings_rev[k])))
        output.write("Saved:%s" % saved)
        
        return output.getvalue()
    
    def dump(self, path):
        data = self.dumps()
        f = open(path, "wb")
        f.write(data)
        f.close()