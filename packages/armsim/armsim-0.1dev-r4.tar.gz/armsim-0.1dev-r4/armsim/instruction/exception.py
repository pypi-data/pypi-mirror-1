"""
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

class ARMBkptInstruction(object):
    implements(IARMInstruction)

    testmask = 0b11111111111100000000000011110000
    bitmask  = 0b11100001001000000000000001110000

    def execute(self, proc, inst):
        print "Ejecutaste un bkpt"

class ARMSwiInstruction(object):
    implements(IARMInstruction)

    testmask = 0b00001111000000000000000000000000
    bitmask  = 0b00001111000000000000000000000000

    def execute(self, proc, inst):
        print "Ejecutaste un swi"

