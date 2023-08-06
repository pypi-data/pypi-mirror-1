#Sempahore Module
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

