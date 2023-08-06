#Status register module
from armsim.interfaces.arminstruction import IARMInstruction
from zope.interface import implements

class ARMMrsInstruction(object):
    implements(IARMInstruction)

    testmask = 0b00001111101100000000000000000000
    bitmask  = 0b00000001000000000000000000000000

    def execute(self, proc, inst):
        print "Ejecutaste un mrs"

class ARMMsriInstruction(object):
    implements(IARMInstruction)

    testmask = 0b00001111101100000000000000000000
    bitmask  = 0b00000011001000000000000000000000

    def execute(self, proc, inst):
        print "Ejecutaste un msri"

class ARMMsrInstruction(object):
    implements(IARMInstruction)

    testmask = 0b00001111101100000000000011110000
    bitmask  = 0b00000001001000000000000000000000

    def execute(self, proc, inst):
        print "Ejecutaste un msr"

