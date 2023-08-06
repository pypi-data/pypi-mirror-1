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
Type classes.
""" 

__all__ = ('LuaTable',
           'Vector',
           'Angle',
           'Player')

class LuaTable(dict):
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        self.last_index = 1
        self.non_keys = []
    
    def append(self, v):
        while self.last_index in self:
            self.last_index = self.last_index + 1
        self[self.last_index] = v
        self.non_keys.append(self.last_index)
        self.last_index = self.last_index + 1
    
    def is_sequential(self):
        return len(self) == len(self.non_keys)

# Vector class from http://code.activestate.com/recipes/52272/
class Vector(list):
    def __init__(self, *args, **kwargs):
        try:
            list.__init__(self, *args, **kwargs)
        except TypeError:
            list.__init__(self, args, **kwargs)
    
    def __getslice__(self, i, j):
        try:
            # use the list __getslice__ method and convert
            # result to vector
            return Vector(super(vector, self).__getslice__(i,j))
        except:
            raise TypeError, 'vector::FAILURE in __getslice__'
        
    def __add__(self, other):
        return Vector(map(lambda x,y: x+y, self, other))

    def __neg__(self):
        return Vector(map(lambda x: -x, self))
    
    def __sub__(self, other):
        return Vector(map(lambda x,y: x-y, self, other))

    def __mul__(self, other):
        """
        Element by element multiplication
        """
        try:
            return Vector(map(lambda x,y: x*y, self,other))
        except:
            # other is a const
            return Vector(map(lambda x: x*other, self))


    def __rmul__(self, other):
        return (self*other)


    def __div__(self, other):
        """
        Element by element division.
        """
        try:
            return Vector(map(lambda x,y: x/y, self, other))
        except:
            return Vector(map(lambda x: x/other, self))

    def __rdiv__(self, other):
        """
        The same as __div__
        """
        
        try:
            return Vector(map(lambda x,y: x/y, other, self))
        except:
            # other is a const
            return Vector(map(lambda x: other/x, self))
    
    def size(self):
        return len(self)

    def conjugate(self):
        return Vector(map(lambda x: x.conjugate(), self))
    
    def reim(self):
        """
        Return the real and imaginary parts
        """
        
        return [
            Vector(map(lambda x: x.real, self)),
            Vector(map(lambda x: x.imag, self)),
            ]
    
    def absarg(self):
        """
        Return modulus and phase parts
        """
        
        return [
            Vector(map(lambda x: abs(x), self)),
            Vector(map(lambda x: math.atan2(x.imag,x.real), self)),
            ]
    
    def str_elements(self):
        return ','.join(map(str, self))
    
    def __repr__(self):
        return "Vector(%s)" % (', '.join(map(str, self)))

class Angle(list):
    def __init__(self, *args, **kwargs):
        try:
            list.__init__(self, *args, **kwargs)
        except TypeError:
            list.__init__(self, args, **kwargs)
    
    def str_elements(self):
        return ','.join(map(str, self))
    
    def __repr__(self):
        return "Angle(%s)" % (', '.join(map(str, self)))

class Player:
    def __init__(self, unique_id):
        self.unique_id = unique_id
    
    def __repr__(self):
        return "Player(%d)" % (self.unique_id)