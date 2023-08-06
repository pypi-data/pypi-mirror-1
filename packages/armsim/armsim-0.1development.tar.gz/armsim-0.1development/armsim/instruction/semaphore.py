"""
Semaphore instruction module
----------------------------

* swp
* swpb

"""
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

