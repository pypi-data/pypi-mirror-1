"""
Semaphore instruction module
----------------------------

* swp
* swpb

"""
#Copyright 2009 armsim authors.
#
#This file is part of armsim.
#
#armsim is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#armsim is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with armsim.  If not, see <http://www.gnu.org/licenses/>.


from armsim.interfaces.arminstruction import IARMInstruction
from zope.interface import implements

class ARMSwpInstruction(object):
    implements(IARMInstruction)

    testmask = 0b00001111111100000000000011110000
    bitmask  = 0b00000001000000000000000010010000

    def execute(self, proc, inst):
        print "Ejecutaste un swp"

class ARMSwpbInstruction(object):
    implements(IARMInstruction)

    testmask = 0b00001111111100000000000011110000
    bitmask  = 0b00000001010000000000000010010000

    def execute(self, proc, inst):
        print "Ejecutaste un swpb"

