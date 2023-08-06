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
