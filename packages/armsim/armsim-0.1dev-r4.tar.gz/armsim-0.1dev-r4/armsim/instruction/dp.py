"""
Data Processing instructions module

Here is where you can find the data processing instructions which are

* and
* eor
* sub

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
from armsim.interfaces.arminstruction import IARMDPAddressingMode
from armsim.utils import checkCondition
from armsim.utils import testInstruction
from armsim.bitset import Bitset
from armsim import utils
from zope.interface import implements
from zope import component

class ARMAndInstruction(object):
    implements(IARMInstruction)

    testmask = 0b00001101111000000000000000000000
    bitmask  = 0b00000000000000000000000000000000

    def execute(self, proc, inst):
        shifter_operand   = 0
        shifter_carry_out = 0
        if not checkCondition(proc, inst):
            return

        S  = utils.getBits(inst, 20)
        I  = utils.getBits(inst, 25)
        rd = utils.getBits(inst, 12, 4)
        rd = 'r' + str(rd)
        rn = utils.getBits(inst, 16, 4)
        rn = 'r' + str(rn)

        modes =  component.getAllUtilitiesRegisteredFor(IARMDPAddressingMode)
        for mode in modes:
            if testInstruction(mode, inst):
                shifter_operand, shifter_carry_out = mode.getVal(proc, inst)
                break

        setattr(proc, rd, getattr(proc, rn) & shifter_operand)
        if S == 1 and rd == 'r15':
            try:
                proc.cpsr = proc.spsr
            except:
                print "UNPREDICTABLE"
        elif S == 1:
            proc.setStatusFlag('N', utils.getBits(getattr(proc, rd), 31))
            proc.setStatusFlag('Z', int(getattr(proc, rd) == 0))
            proc.setStatusFlag('C', shifter_carry_out)

class ARMEorInstruction(object):
    implements(IARMInstruction)

    testmask = 0b00001101111000000000000000000000
    bitmask  = 0b00000000001000000000000000000000

    def execute(self, proc, inst):
        shifter_operand   = 0
        shifter_carry_out = 0
        if not checkCondition(proc, inst):
            return

        S  = utils.getBits(inst, 20)
        I  = utils.getBits(inst, 25)
        rd = utils.getBits(inst, 12, 4)
        rd = 'r' + str(rd)
        rn = utils.getBits(inst, 16, 4)
        rn = 'r' + str(rn)
        rdVal = getattr(proc, rd)
        rnVal = getattr(proc, rn)

        modes =  component.getAllUtilitiesRegisteredFor(IARMDPAddressingMode)
        for mode in modes:
            if testInstruction(mode, inst):
                shifter_operand, shifter_carry_out = mode.getVal(proc, inst)
                break

        setattr(proc, rd, rnVal ^ shifter_operand)
        if S == 1 and rd == 'r15':
            try:
                proc.cpsr = proc.spsr
            except:
                print "UNPREDICTABLE"
        elif S == 1:
            proc.setStatusFlag('N', utils.getBits(getattr(proc, rd), 31))
            proc.setStatusFlag('Z', int(getattr(proc, rd) == 0))
            proc.setStatusFlag('C', shifter_carry_out)
        


class ARMSubInstruction(object):
    implements(IARMInstruction)

    testmask = 0b00001101111000000000000000000000
    bitmask  = 0b00000000010000000000000000000000

    def execute(self, proc, inst):
        shifter_operand   = 0
        shifter_carry_out = 0
        if not checkCondition(proc, inst):
            return

        S  = utils.getBits(inst, 20)
        I  = utils.getBits(inst, 25)
        rd = utils.getBits(inst, 12, 4)
        rd = 'r' + str(rd)
        rn = utils.getBits(inst, 16, 4)
        rn = 'r' + str(rn)
        rdVal = getattr(proc, rd)
        rnVal = getattr(proc, rn)
        rnBitset = Bitset(rnVal, 32)

        modes =  component.getAllUtilitiesRegisteredFor(IARMDPAddressingMode)
        for mode in modes:
            if testInstruction(mode, inst):
                shifter_operand, shifter_carry_out = mode.getVal(proc, inst)
                break
        
        shifter_bitset = Bitset(shifter_operand, 32)

        result, borrow = rnBitset - shifter_bitset
        setattr(proc, rd, int(result))

        if S == 1 and rd == 'r15':
            try:
                proc.cpsr = proc.spsr
            except:
                print "UNPREDICTABLE"
        elif S == 1:
            if utils.getBits(rdVal, 31) == 0 and utils.getBits(int(result), 31) == 1:
                v = 1
            else:
                v = 0
            proc.setStatusFlag('N', utils.getBits(getattr(proc, rd), 31))
            proc.setStatusFlag('Z', int(getattr(proc, rd) == 0))
            proc.setStatusFlag('C', int(borrow == 0))
            proc.setStatusFlag('V', v)

class ARMRsbInstruction(object):
    implements(IARMInstruction)

    testmask = 0b00001101111000000000000000000000
    bitmask  = 0b00000000011000000000000000000000

    def execute(self, proc, inst):
        shifter_operand   = 0
        shifter_carry_out = 0
        if not checkCondition(proc, inst):
            return

        S  = utils.getBits(inst, 20)
        I  = utils.getBits(inst, 25)
        rd = utils.getBits(inst, 12, 4)
        rd = 'r' + str(rd)
        rn = utils.getBits(inst, 16, 4)
        rn = 'r' + str(rn)
        rdVal = getattr(proc, rd)
        rnVal = getattr(proc, rn)
        rnBitset = Bitset(rnVal, 32)

        modes =  component.getAllUtilitiesRegisteredFor(IARMDPAddressingMode)
        for mode in modes:
            if testInstruction(mode, inst):
                shifter_operand, shifter_carry_out = mode.getVal(proc, inst)
                break
        
        shifter_bitset = Bitset(shifter_operand, 32)

        result, borrow = rshifter_bitset - rnBitset
        setattr(proc, rd, int(result))

        if S == 1 and rd == 'r15':
            try:
                proc.cpsr = proc.spsr
            except:
                print "UNPREDICTABLE"
        elif S == 1:
            if utils.getBits(shifter_operand, 31) == 0 and utils.getBits(int(result), 31) == 1:
                v = 1
            else:
                v = 0
            proc.setStatusFlag('N', utils.getBits(getattr(proc, rd), 31))
            proc.setStatusFlag('Z', int(getattr(proc, rd) == 0))
            proc.setStatusFlag('C', int(borrow == 0))
            proc.setStatusFlag('V', v)

class ARMAddInstruction(object):
    implements(IARMInstruction)

    testmask = 0b00001101111000000000000000000000
    bitmask  = 0b00000000100000000000000000000000

    def execute(self, proc, inst):
        shifter_operand   = 0
        shifter_carry_out = 0
        if not checkCondition(proc, inst):
            return

        S  = utils.getBits(inst, 20)
        I  = utils.getBits(inst, 25)
        rd = utils.getBits(inst, 12, 4)
        rd = 'r' + str(rd)
        rn = utils.getBits(inst, 16, 4)
        rn = 'r' + str(rn)
        rdVal = getattr(proc, rd)
        rnVal = getattr(proc, rn)
        rnBitset = Bitset(rnVal, 32)

        modes =  component.getAllUtilitiesRegisteredFor(IARMDPAddressingMode)
        for mode in modes:
            if testInstruction(mode, inst):
                shifter_operand, shifter_carry_out = mode.getVal(proc, inst)
                break
        
        shifter_bitset = Bitset(shifter_operand, 32)

        result, carry = rnBitset + shifter_bitset
        setattr(proc, rd, int(result))

        if S == 1 and rd == 'r15':
            try:
                proc.cpsr = proc.spsr
            except:
                print "UNPREDICTABLE"
        elif S == 1:
            if utils.getBits(rdVal, 31) == 0 and utils.getBits(int(result), 31) == 1:
                v = 1
            else:
                v = 0
            proc.setStatusFlag('N', utils.getBits(getattr(proc, rd), 31))
            proc.setStatusFlag('Z', int(getattr(proc, rd) == 0))
            proc.setStatusFlag('C', carry)
            proc.setStatusFlag('V', v)

class ARMAdcInstruction(object):
    implements(IARMInstruction)

    testmask = 0b00001101111000000000000000000000
    bitmask  = 0b00000000101000000000000000000000

    def execute(self, proc, inst):
        shifter_operand   = 0
        shifter_carry_out = 0
        if not checkCondition(proc, inst):
            return

        S  = utils.getBits(inst, 20)
        I  = utils.getBits(inst, 25)
        rd = utils.getBits(inst, 12, 4)
        rd = 'r' + str(rd)
        rn = utils.getBits(inst, 16, 4)
        rn = 'r' + str(rn)
        rdVal = getattr(proc, rd)
        rnVal = getattr(proc, rn)
        rnBitset = Bitset(rnVal, 32)
        carryBitset = Bitset(proc.statusFlag('C'), 32)

        modes =  component.getAllUtilitiesRegisteredFor(IARMDPAddressingMode)
        for mode in modes:
            if testInstruction(mode, inst):
                shifter_operand, shifter_carry_out = mode.getVal(proc, inst)
                break
        
        shifter_bitset = Bitset(shifter_operand, 32)

        result, carry = rnBitset + shifter_bitset
        resultBitset  = Bitset(result, 32)
        result, carry = resultBitset + carryBitset
        setattr(proc, rd, int(result))

        if S == 1 and rd == 'r15':
            try:
                proc.cpsr = proc.spsr
            except:
                print "UNPREDICTABLE"
        elif S == 1:
            if utils.getBits(rdVal, 31) == 0 and utils.getBits(int(result), 31) == 1:
                v = 1
            else:
                v = 0
            proc.setStatusFlag('N', utils.getBits(getattr(proc, rd), 31))
            proc.setStatusFlag('Z', int(getattr(proc, rd) == 0))
            proc.setStatusFlag('C', carry)
            proc.setStatusFlag('V', v)

class ARMSbcInstruction(object):
    implements(IARMInstruction)

    testmask = 0b00001101111000000000000000000000
    bitmask  = 0b00000000110000000000000000000000

    def execute(self, proc, inst):
        shifter_operand   = 0
        shifter_carry_out = 0
        if not checkCondition(proc, inst):
            return

        S  = utils.getBits(inst, 20)
        I  = utils.getBits(inst, 25)
        rd = utils.getBits(inst, 12, 4)
        rd = 'r' + str(rd)
        rn = utils.getBits(inst, 16, 4)
        rn = 'r' + str(rn)
        rdVal = getattr(proc, rd)
        rnVal = getattr(proc, rn)
        rnBitset = Bitset(rnVal, 32)
        carryBitset = Bitset(proc.statusFlag('C'), 32)

        modes =  component.getAllUtilitiesRegisteredFor(IARMDPAddressingMode)
        for mode in modes:
            if testInstruction(mode, inst):
                shifter_operand, shifter_carry_out = mode.getVal(proc, inst)
                break
        
        shifter_bitset = Bitset(shifter_operand, 32)

        result, carry = rnBitset - shifter_bitset
        resultBitset  = Bitset(result, 32)
        carryBitset[0] = not carryBitset[0]
        result, carry = resultBitset - carryBitset
        setattr(proc, rd, int(result))

        if S == 1 and rd == 'r15':
            try:
                proc.cpsr = proc.spsr
            except:
                print "UNPREDICTABLE"
        elif S == 1:
            if utils.getBits(rdVal, 31) == 0 and utils.getBits(int(result), 31) == 1:
                v = 1
            else:
                v = 0
            proc.setStatusFlag('N', utils.getBits(getattr(proc, rd), 31))
            proc.setStatusFlag('Z', int(getattr(proc, rd) == 0))
            proc.setStatusFlag('C', int(carry == 0))
            proc.setStatusFlag('V', v)

class ARMRscInstruction(object):
    implements(IARMInstruction)

    testmask = 0b00001101111000000000000000000000
    bitmask  = 0b00000000111000000000000000000000

    def execute(self, proc, inst):
        shifter_operand   = 0
        shifter_carry_out = 0
        if not checkCondition(proc, inst):
            return

        S  = utils.getBits(inst, 20)
        I  = utils.getBits(inst, 25)
        rd = utils.getBits(inst, 12, 4)
        rd = 'r' + str(rd)
        rn = utils.getBits(inst, 16, 4)
        rn = 'r' + str(rn)
        rdVal = getattr(proc, rd)
        rnVal = getattr(proc, rn)
        rnBitset = Bitset(rnVal, 32)
        carryBitset = Bitset(proc.statusFlag('C'), 32)

        modes =  component.getAllUtilitiesRegisteredFor(IARMDPAddressingMode)
        for mode in modes:
            if testInstruction(mode, inst):
                shifter_operand, shifter_carry_out = mode.getVal(proc, inst)
                break
        
        shifter_bitset = Bitset(shifter_operand, 32)

        result, carry = shifter_bitset - rnBitset
        resultBitset  = Bitset(result, 32)
        carryBitset[0] = not carryBitset[0]
        result, carry = resultBitset - carryBitset
        setattr(proc, rd, int(result))

        if S == 1 and rd == 'r15':
            try:
                proc.cpsr = proc.spsr
            except:
                print "UNPREDICTABLE"
        elif S == 1:
            if utils.getBits(rdVal, 31) == 0 and utils.getBits(int(result), 31) == 1:
                v = 1
            else:
                v = 0
            proc.setStatusFlag('N', utils.getBits(getattr(proc, rd), 31))
            proc.setStatusFlag('Z', int(getattr(proc, rd) == 0))
            proc.setStatusFlag('C', int(carry == 0))
            proc.setStatusFlag('V', v)
        print "Ejecutaste un rsc"

class ARMTstInstruction(object):
    implements(IARMInstruction)

    testmask = 0b00001101111100000000000000000000
    bitmask  = 0b00000001000100000000000000000000

    def execute(self, proc, inst):
        shifter_operand   = 0
        shifter_carry_out = 0
        if not checkCondition(proc, inst):
            return

        rn = utils.getBits(inst, 16, 4)
        rn = 'r' + str(rn)
        rnVal = getattr(proc, rn)

        modes =  component.getAllUtilitiesRegisteredFor(IARMDPAddressingMode)
        for mode in modes:
            if testInstruction(mode, inst):
                shifter_operand, shifter_carry_out = mode.getVal(proc, inst)
                break

        alu_out = rnVal & shifter_operand

        
        proc.setStatusFlag('N', utils.getBits(alu_out, 31))
        proc.setStatusFlag('Z', int(alu_out == 0))
        proc.setStatusFlag('C', shifter_carry_out)

class ARMTeqInstruction(object):
    implements(IARMInstruction)

    testmask = 0b00001101111100000000000000000000
    bitmask  = 0b00000001001100000000000000000000

    def execute(self, proc, inst):
        shifter_operand   = 0
        shifter_carry_out = 0
        if not checkCondition(proc, inst):
            return

        rn = utils.getBits(inst, 16, 4)
        rn = 'r' + str(rn)
        rnVal = getattr(proc, rn)

        modes =  component.getAllUtilitiesRegisteredFor(IARMDPAddressingMode)
        for mode in modes:
            if testInstruction(mode, inst):
                shifter_operand, shifter_carry_out = mode.getVal(proc, inst)
                break

        alu_out = rnVal ^ shifter_operand
        
        proc.setStatusFlag('N', utils.getBits(alu_out, 31))
        proc.setStatusFlag('Z', int(alu_out == 0))
        proc.setStatusFlag('C', shifter_carry_out)

class ARMCmpInstruction(object):
    implements(IARMInstruction)

    testmask = 0b00001101111100000000000000000000
    bitmask  = 0b00000001010100000000000000000000

    def execute(self, proc, inst):
        shifter_operand   = 0
        shifter_carry_out = 0
        if not checkCondition(proc, inst):
            return

        rn = utils.getBits(inst, 16, 4)
        rn = 'r' + str(rn)
        rnVal = getattr(proc, rn)

        modes =  component.getAllUtilitiesRegisteredFor(IARMDPAddressingMode)
        for mode in modes:
            if testInstruction(mode, inst):
                shifter_operand, shifter_carry_out = mode.getVal(proc, inst)
                break

        rnBitset      = Bitset(rnVal, 32)
        shifterBitset = Bitset(shifter_operand, 32)
        alu_out, borrow = rnBitset - shifterBitset
        
        if utils.getBits(rnVal, 31) == 0 and utils.getBits(int(alu_out), 31) == 1:
            v = 1
        else:
            v = 0
        proc.setStatusFlag('N', utils.getBits(int(alu_out), 31))
        proc.setStatusFlag('Z', int(int(alu_out) == 0))
        proc.setStatusFlag('C', int(borrow == 0))
        proc.setStatusFlag('V', v)

class ARMCmnInstruction(object):
    implements(IARMInstruction)

    testmask = 0b00001101111100000000000000000000
    bitmask  = 0b00000001011100000000000000000000

    def execute(self, proc, inst):
        shifter_operand   = 0
        shifter_carry_out = 0
        if not checkCondition(proc, inst):
            return

        rn = utils.getBits(inst, 16, 4)
        rn = 'r' + str(rn)
        rnVal = getattr(proc, rn)

        modes =  component.getAllUtilitiesRegisteredFor(IARMDPAddressingMode)
        for mode in modes:
            if testInstruction(mode, inst):
                shifter_operand, shifter_carry_out = mode.getVal(proc, inst)
                break

        rnBitset      = Bitset(rnVal, 32)
        shifterBitset = Bitset(shifter_operand, 32)
        alu_out, carry = rnBitset + shifter_operand
        
        if utils.getBits(rdVal, 31) == 0 and utils.getBits(int(result), 31) == 1:
            v = 1
        else:
            v = 0
        proc.setStatusFlag('N', utils.getBits(int(alu_out), 31))
        proc.setStatusFlag('Z', int(int(alu_out) == 0))
        proc.setStatusFlag('C', carry)
        proc.setStatusFlag('V', v)

class ARMOrrInstruction(object):
    implements(IARMInstruction)

    testmask = 0b00001101111000000000000000000000
    bitmask  = 0b00000001100000000000000000000000

    def execute(self, proc, inst):
        shifter_operand   = 0
        shifter_carry_out = 0
        if not checkCondition(proc, inst):
            return

        S  = utils.getBits(inst, 20)
        I  = utils.getBits(inst, 25)
        rd = utils.getBits(inst, 12, 4)
        rd = 'r' + str(rd)
        rn = utils.getBits(inst, 16, 4)
        rn = 'r' + str(rn)

        modes =  component.getAllUtilitiesRegisteredFor(IARMDPAddressingMode)
        for mode in modes:
            if testInstruction(mode, inst):
                shifter_operand, shifter_carry_out = mode.getVal(proc, inst)
                break

        setattr(proc, rd, getattr(proc, rn) | shifter_operand)
        if S == 1 and rd == 'r15':
            try:
                proc.cpsr = proc.spsr
            except:
                print "UNPREDICTABLE"
        elif S == 1:
            proc.setStatusFlag('N', utils.getBits(getattr(proc, rd), 31))
            proc.setStatusFlag('Z', int(getattr(proc, rd) == 0))
            proc.setStatusFlag('C', shifter_carry_out)

        print "Ejecutaste un orr"

class ARMMovInstruction(object):
    implements(IARMInstruction)

    testmask = 0b00001101111000000000000000000000
    bitmask  = 0b00000001101000000000000000000000

    def execute(self, proc, inst):
        shifter_operand   = 0
        shifter_carry_out = 0
        if not checkCondition(proc, inst):
            return

        S  = utils.getBits(inst, 20)
        I  = utils.getBits(inst, 25)
        rd = utils.getBits(inst, 12, 4)
        rd = 'r' + str(rd)

        modes =  component.getAllUtilitiesRegisteredFor(IARMDPAddressingMode)
        for mode in modes:
            if testInstruction(mode, inst):
                shifter_operand, shifter_carry_out = mode.getVal(proc, inst)
                break
                
        setattr(proc, rd, shifter_operand)

        if S == 1 and rd == 'r15':
            try:
                proc.cpsr = spsr
            except:
                print "UNPREDICTABLE"
        elif S == 1:
            proc.setStatusFlag('N', utils.getBits(shifter_operand, 31))
            proc.setStatusFlag('Z', int(shifter_operand == 0))
            proc.setStatusFlag('C', shifter_carry_out)

class ARMBicInstruction(object):
    implements(IARMInstruction)

    testmask = 0b00001101111000000000000000000000
    bitmask  = 0b00000001110000000000000000000000

    def execute(self, proc, inst):
        shifter_operand   = 0
        shifter_carry_out = 0
        if not checkCondition(proc, inst):
            return

        S  = utils.getBits(inst, 20)
        I  = utils.getBits(inst, 25)
        rd = utils.getBits(inst, 12, 4)
        rd = 'r' + str(rd)
        rn = utils.getBits(inst, 16, 4)
        rn = 'r' + str(rn)

        modes =  component.getAllUtilitiesRegisteredFor(IARMDPAddressingMode)
        for mode in modes:
            if testInstruction(mode, inst):
                shifter_operand, shifter_carry_out = mode.getVal(proc, inst)
                break

        shifterBitset = Bitset(shifter_operand, 32)
        shifter_operand = int(~shifterBitset)
	
        setattr(proc, rd, getattr(proc, rn) & shifter_operand)
        if S == 1 and rd == 'r15':
            try:
                proc.cpsr = proc.spsr
            except:
                print "UNPREDICTABLE"
        elif S == 1:
            proc.setStatusFlag('N', utils.getBits(getattr(proc, rd), 31))
            proc.setStatusFlag('Z', int(getattr(proc, rd) == 0))
            proc.setStatusFlag('C', shifter_carry_out)

class ARMMvnInstruction(object):
    implements(IARMInstruction)

    testmask = 0b00001101111000000000000000000000
    bitmask  = 0b00000001111000000000000000000000

    def execute(self, proc, inst):
        shifter_operand   = 0
        shifter_carry_out = 0
        if not checkCondition(proc, inst):
            return

        S  = utils.getBits(inst, 20)
        I  = utils.getBits(inst, 25)
        rd = utils.getBits(inst, 12, 4)
        rd = 'r' + str(rd)

        modes =  component.getAllUtilitiesRegisteredFor(IARMDPAddressingMode)
        for mode in modes:
            if testInstruction(mode, inst):
                shifter_operand, shifter_carry_out = mode.getVal(proc, inst)
                break

        shifterBitset = Bitset(shifter_operand, 32)
        shifter_operand = int(~shifterBitset)
                
        setattr(proc, rd, shifter_operand)

        if S == 1 and rd == 'r15':
            try:
                proc.cpsr = spsr
            except:
                print "UNPREDICTABLE"
        elif S == 1:
            proc.setStatusFlag('N', utils.getBits(shifter_operand, 31))
            proc.setStatusFlag('Z', int(shifter_operand == 0))
            proc.setStatusFlag('C', shifter_carry_out)


class ARMDPAddressingMode1(object):
    implements(IARMDPAddressingMode)

    testmask = 0b00001110000000000000000000000000
    bitmask  = 0b00000010000000000000000000000000

    def getVal(self, proc, inst):
        rotate_imm = utils.getBits(inst, 8, 4)
        immed_8    = utils.getBits(inst, 0, 8)
        shifter_operand = utils.ror(immed_8, 32, rotate_imm * 2)
        if rotate_imm == 0:
            shifter_carry_out = proc.statusFlag('C')
        else:
            shifter_carry_out = utils.getBits(shifter_operand, 31)
        return (shifter_operand, shifter_carry_out)

class ARMDPAddressingMode2(object):
    implements(IARMDPAddressingMode)

    testmask = 0b00001110000000000000111111110000
    bitmask  = 0b00000000000000000000000000000000

    def getVal(self, proc, inst):
        rm = utils.getBits(inst, 0, 4)
        rm = 'r' + str(rm)
        shifter_operand = getattr(proc, rm)
        shifter_carry_out = proc.statusFlag('C')
        return (shifter_operand, shifter_carry_out)

class ARMDPAddressingMode3(object):
    implements(IARMDPAddressingMode)

    testmask = 0b00001110000000000000000001110000
    bitmask  = 0b00000000000000000000000000000000

    def getVal(self, proc, inst):
        rm = utils.getBits(inst, 0, 4)
        rm = 'r' + str(rm)
        shift_imm = utils.getBits(inst, 7, 5)
        if shift_imm == 0:
            shifter_operand = getattr(proc, rm)
            shifter_carry_out = proc.statusFlag('C')
        else:
            shifter_operand = getattr(proc, rm) << shift_imm
            shifter_operand = shifter_operand & 0xFFFFFFFF
            shifter_carry_out = utils.getBits(getattr(proc, rm), 32 - shift_imm)
        
        return (shifter_operand, shifter_carry_out)

class ARMDPAddressingMode4(object):
    implements(IARMDPAddressingMode)

    testmask = 0b00001110000000000000000011110000
    bitmask  = 0b00000000000000000000000000010000

    def getVal(self, proc, inst):
        rm = utils.getBits(inst, 0, 4)
        rm = 'r' + str(rm)
        rs = utils.getBits(inst, 8, 4)
        rs = 'r' + str(rs)
        rs_val = utils.getBits(getattr(proc, rs), 0, 8)
        if rs_val == 0:
            shifter_operand = getattr(proc, rm)
            shifter_carry_out = proc.statusFlag('C')
        elif rs_val < 32:
            shifter_operand = getattr(proc, rm) << rs_val
            shifter_operand = shifter_operand & 0xFFFFFFFF
            shifter_carry_out = utils.getBits(getattr(proc, rm), 32 - rs_val)
        elif rs_val == 32:
            shifter_operand = 0
            shifter_carry_out = utils.getBits(getattr(proc, rm), 0)
        else:
            shifter_operand = 0
            shifter_carry_out = 0 
            
        return (shifter_operand, shifter_carry_out)
        
        

class ARMDPAddressingMode5(object):
    implements(IARMDPAddressingMode)

    testmask = 0b00001110000000000000000001110000
    bitmask  = 0b00000000000000000000000000100000

    def getVal(self, proc, inst):
        rm = utils.getBits(inst, 0, 4)
        rm = 'r' + str(rm)
        shift_imm = utils.getBits(inst, 7, 5)
        if shift_imm == 0:
            shifter_operand = getattr(proc, rm)
            shifter_carry_out = utils.getBits(getattr(proc, rm), 31)
        else:
            shifter_operand = getattr(proc, rm) >> shift_imm
            shifter_carry_out = utils.getBits(getattr(proc, rm), shift_imm - 1)
        
        return (shifter_operand, shifter_carry_out)

class ARMDPAddressingMode6(object):
    implements(IARMDPAddressingMode)

    testmask = 0b00001110000000000000000011110000
    bitmask  = 0b00000000000000000000000000110000

    def getVal(self, proc, inst):
        rm = utils.getBits(inst, 0, 4)
        rm = 'r' + str(rm)
        rs = utils.getBits(inst, 8, 4)
        rs = 'r' + str(rs)
        rs_val = utils.getBits(getattr(proc, rs), 0, 8)
        if rs_val == 0:
            shifter_operand = getattr(proc, rm)
            shifter_carry_out = proc.statusFlag('C')
        elif rs_val < 32:
            shifter_operand = getattr(proc, rm) >> rs_val
            shifter_carry_out = utils.getBits(getattr(proc, rm), rs_val - 1)
        elif rs_val == 32:
            shifter_operand = 0
            shifter_carry_out = utils.getBits(getattr(proc, rm), 1)
        else:
            shifter_operand = 0
            shifter_carry_out = 0 
            
        return (shifter_operand, shifter_carry_out)

class ARMDPAddressingMode7(object):
    implements(IARMDPAddressingMode)

    testmask = 0b00001110000000000000000001110000
    bitmask  = 0b00000000000000000000000001000000

    def getVal(self, proc, inst):
        rm = utils.getBits(inst, 0, 4)
        rm = 'r' + str(rm)
        rmVal = getattr(proc, rm)
        shift_imm = utils.getBits(inst, 7, 5)
        if shift_imm == 0:
            if utils.getBits(rmVal, 31) == 0:
                shifter_operand = 0
                shifter_carry_out = utils.getBits(rmVal, 31)
            else:
                shifter_operand = 0xFFFFFFFF
                shifter_carry_out = utils.getBits(rmVal, 31)
        else:
            shifter_operand = utils.asr(rmVal, shift_imm)
            shifter_carry_out = utils.getBits(rmVal, shift_imm - 1)
    
        return (shifter_operand, shifter_carry_out)

class ARMDPAddressingMode8(object):
    implements(IARMDPAddressingMode)

    testmask = 0b00001110000000000000000011110000
    bitmask  = 0b00000000000000000000000001010000

    def getVal(self, proc, inst):
        rm = utils.getBits(inst, 0, 4)
        rm = 'r' + str(rm)
        rs = utils.getBits(inst, 8, 4)
        rs = 'r' + str(rs)
        rs_val = utils.getBits(getattr(proc, rs), 0, 8)
        if rs_val == 0:
            shifter_operand = getattr(proc, rm)
            shifter_carry_out = proc.statusFlag('C')
        elif rs_val < 32:
            shifter_operand = utils.asr(getattr(proc, rm), rs_val)
            shifter_carry_out = utils.getBits(getattr(proc, rm), rs_val - 1)
        else:
            if utils.getBits(getattr(proc, rm), 31) == 0:
                shifter_operand = 0
                shifter_carry_out = utils.getBits(getattr(proc, rm), 31)
            else:
                shifter_operand = 0xFFFFFFFF
                shifter_carry_out = utils.getBits(getattr(proc, rm), 31)

        return (shifter_operand, shifter_carry_out)

class ARMDPAddressingMode9(object):
    implements(IARMDPAddressingMode)

    testmask = 0b00001110000000000000000001110000
    bitmask  = 0b00000000000000000000000001100000

    def getVal(self, proc, inst):
        rm = utils.getBits(inst, 0, 4)
        rm = 'r' + str(rm)
        rmVal = getattr(proc, rm)
        shift_imm = utils.getBits(inst, 7, 5)
        if shift_imm == 0:
            operand1 = proc.statusFlag('C') << 31
            operand1 = operand1 & 0xFFFFFFFF
            operand2 = rmVal >> 1
            shifter_operand = operand1 | operand2
            shifter_carry_out = utils.getBits(rmVal, 0)
        else:
            shifter_operand = utils.ror(rmVal, 32, shift_imm)
            shifter_carry_out = utils.getBits(rmVal, shift_imm - 1)

        return (shifter_operand, shifter_carry_out)

class ARMDPAddressingMode10(object):
    implements(IARMDPAddressingMode)

    testmask = 0b00001110000000000000000011110000
    bitmask  = 0b00000000000000000000000001110000

    def getVal(self, proc, inst):
        rm = utils.getBits(inst, 0, 4)
        rm = 'r' + str(rm)
        rs = utils.getBits(inst, 8, 4)
        rs = 'r' + str(rs)
        rs_val = utils.getBits(getattr(proc, rs), 0, 8)
        rs_val2 = utils.getBits(getattr(proc, rs), 0, 5)
        if rs_val == 0:
            shifter_operand = getattr(proc, rm)
            shifter_carry_out = proc.statusFlag('C')
        elif rs_val2 == 0:
            shifter_operand = getattr(proc, rm)
            shifter_carry_out = utils.getBits(getattr(proc, rm), 31)
        else:
            shifter_operand = utils.ror(getattr(proc, rm), 32, rs_val2)
            shifter_carry_out = utils.getBits(getattr(proc, rm), rs_val2 - 1)

        return (shifter_operand, shifter_carry_out)

