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


from zope.interface import Interface
from zope.interface import Attribute

class IARMInstruction(Interface):
    """This interface defines the ARM instruction"""

    testmask = Attribute("Bits to test to check instruction type")
    bitmask  = Attribute("Value to test to check instruction type")
    
    def execute(proc, inst):
        """Executes the instruction"""

class IARMDPAddressingMode(Interface):
    """This interface defines the ARM Data processing addressing mode"""

    testmask = Attribute("Bits to test to check instruction type")
    bitmask  = Attribute("Value to test to check instruction type")
    
    def getVal(proc, inst):
        """Gets value of addressing mode"""

class IARMLSAddressingMode(Interface):
    """This interface defines the ARM Load Store addressing mode"""

    testmask = Attribute("Bits to test to check instruction type")
    bitmask  = Attribute("Value to test to check instruction type")
    
    def getVal(proc, inst):
        """Gets value of addressing mode"""

class IARMLSMAddressingMode(Interface):
    """This interface defines the ARM Load Store Multiple addressing mode"""

    testmask = Attribute("Bits to test to check instruction type")
    bitmask  = Attribute("Value to test to check instruction type")
    
    def getVal(proc, inst):
        """Gets value of addressing mode"""
