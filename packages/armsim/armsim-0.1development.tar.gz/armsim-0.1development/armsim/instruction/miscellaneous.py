#Miscellaneous Module
from armsim.interfaces.arminstruction import IARMInstruction
from zope.interface import implements

class ARMClzInstruction(object):
    implements(IARMInstruction)

    testmask = 0b00001111111100000000000000000000
    bitmask  = 0b00000001011000000000000000000000

    def execute(self, proc, inst):
        print "Ejecutaste un clz"

