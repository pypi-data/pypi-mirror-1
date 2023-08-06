"""
Load and store instructions
---------------------------
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
from armsim.interfaces.arminstruction import IARMLSAddressingMode
from armsim.interfaces.arminstruction import IARMLSMAddressingMode
from armsim import exceptions
from zope.interface import implements
from zope import component
from armsim import utils
from armsim.bitset import Bitset

class ARMLdm1Instruction(object):
    implements(IARMInstruction)

    testmask = 0b00001110010100000000000000000000
    bitmask  = 0b00001000000100000000000000000000

    def execute(self, proc, inst):
        if not utils.checkCondition(proc, inst):
            return

        modes =  component.getAllUtilitiesRegisteredFor(IARMLSMAddressingMode)
        for mode in modes:
            if utils.testInstruction(mode, inst):
                start_address, end_address = mode.getVal(proc, inst)
                break

        register_list = Bitset(utils.getBits(inst, 0, 16), 32)

        address = start_address
  
        for i in range(15):
            if register_list[i]:
                setattr(proc, 'r' + str(i), proc.readAddr(address, 4))
                address += 4

        if register_list[15]:
            value = proc.readAddr(address, 4)
            proc.pc = value & 0xFFFFFFFE
            address += 4

        if end_address != address - 4:
            raise exceptions.DataAbort()

class ARMLdm2Instruction(object):
    implements(IARMInstruction)

    testmask = 0b00001110011100001000000000000000
    bitmask  = 0b00001000010100000000000000000000

    def execute(self, proc, inst):
        if not utils.checkCondition(proc, inst):
            return

        modes =  component.getAllUtilitiesRegisteredFor(IARMLSMAddressingMode)
        for mode in modes:
            if utils.testInstruction(mode, inst):
                start_address, end_address = mode.getVal(proc, inst)
                break
        print "Ejecutaste un ldm(2)"

class ARMLdm3Instruction(object):
    implements(IARMInstruction)

    testmask = 0b00001110010100001000000000000000
    bitmask  = 0b00001000010100001000000000000000

    def execute(self, proc, inst):
        if not utils.checkCondition(proc, inst):
            return

        modes =  component.getAllUtilitiesRegisteredFor(IARMLSMAddressingMode)
        for mode in modes:
            if utils.testInstruction(mode, inst):
                start_address, end_address = mode.getVal(proc, inst)
                break
        print "Ejecutaste un ldm(3)"

class ARMLdrInstruction(object):
    implements(IARMInstruction)

    testmask = 0b00001100010100000000000000000000
    bitmask  = 0b00000100000100000000000000000000

    def execute(self, proc, inst):
        if not utils.checkCondition(proc, inst):
            return

        modes =  component.getAllUtilitiesRegisteredFor(IARMLSAddressingMode)
        for mode in modes:
            if utils.testInstruction(mode, inst):
                address = mode.getVal(proc, inst)
                break
        rd = utils.getBits(inst, 12, 4)
        rd = 'r' + str(rd)

        data = proc.readAddr(address)

        if rd == 'r15':
            proc.pc = data & 0xfffffffe
        else:
            setattr(proc, rd, data)

class ARMLdrbInstruction(object):
    implements(IARMInstruction)

    testmask = 0b00001100010100000000000000000000
    bitmask  = 0b00000100010100000000000000000000

    def execute(self, proc, inst):
        if not utils.checkCondition(proc, inst):
            return

        modes =  component.getAllUtilitiesRegisteredFor(IARMLSAddressingMode)
        for mode in modes:
            if utils.testInstruction(mode, inst):
                address = mode.getVal(proc, inst)
                break
        rd = utils.getBits(inst, 12, 4)
        rd = 'r' + str(rd)

        data = proc.readAddr(address, 1)

        setattr(proc, rd, data)

class ARMLdrbtInstruction(object):
    implements(IARMInstruction)

    testmask = 0b00001101011100000000000000000000
    bitmask  = 0b00000100011100000000000000000000

    def execute(self, proc, inst):
        if not utils.checkCondition(proc, inst):
            return

        modes =  component.getAllUtilitiesRegisteredFor(IARMLSAddressingMode)
        for mode in modes:
            if utils.testInstruction(mode, inst):
                address = mode.getVal(proc, inst)
                break
        rd = utils.getBits(inst, 12, 4)
        rd = 'r' + str(rd)
        rn = utils.getBits(inst, 16, 4)
        rn = 'r' + str(rn)

        data = proc.readAddr(address, 1)
        setattr(proc, rd, data)
        setattr(proc, rn, address)

class ARMLdrdInstruction(object):
    implements(IARMInstruction)

    testmask = 0b00001110000100000000000011110000
    bitmask  = 0b00000000000000000000000011010000

    def execute(self, proc, inst):
        if not utils.checkCondition(proc, inst):
            return

        modes =  component.getAllUtilitiesRegisteredFor(IARMLSAddressingMode)
        for mode in modes:
            if utils.testInstruction(mode, inst):
                address = mode.getVal(proc, inst)
                break
        rd = utils.getBits(inst, 12, 4)
        rn = rd + 1
        rd = 'r' + str(rd)
        rn = 'r' + str(rn)

        data = proc.readAddr(address)
        setattr(proc, rd, data)
        data = proc.readAddr(address+4)
        setattr(proc, rn, data)

class ARMLdrhInstruction(object):
    implements(IARMInstruction)

    testmask = 0b00001110000100000000000011110000
    bitmask  = 0b00000000000100000000000010110000

    def execute(self, proc, inst):
        if not utils.checkCondition(proc, inst):
            return

        modes =  component.getAllUtilitiesRegisteredFor(IARMLSAddressingMode)
        for mode in modes:
            if utils.testInstruction(mode, inst):
                address = mode.getVal(proc, inst)
                break
        rd = utils.getBits(inst, 12, 4)
        rd = 'r' + str(rd)

        data = proc.readAddr(address, 2)
        setattr(proc, rd, data)

class ARMLdrsbInstruction(object):
    implements(IARMInstruction)

    testmask = 0b00001110000100000000000011110000
    bitmask  = 0b00000000000100000000000011010000

    def execute(self, proc, inst):
        if not utils.checkCondition(proc, inst):
            return

        modes =  component.getAllUtilitiesRegisteredFor(IARMLSAddressingMode)
        for mode in modes:
            if utils.testInstruction(mode, inst):
                address = mode.getVal(proc, inst)
                break
        rd = utils.getBits(inst, 12, 4)
        rd = 'r' + str(rd)

        data = proc.readAddr(address, 1)
        data = utils.signExtend(data, 8, 32)

        setattr(proc, rd, data)

class ARMLdrshInstruction(object):
    implements(IARMInstruction)

    testmask = 0b00001110000100000000000011110000
    bitmask  = 0b00000000000100000000000011110000

    def execute(self, proc, inst):
        if not utils.checkCondition(proc, inst):
            return

        modes =  component.getAllUtilitiesRegisteredFor(IARMLSAddressingMode)
        for mode in modes:
            if utils.testInstruction(mode, inst):
                address = mode.getVal(proc, inst)
                break
        rd = utils.getBits(inst, 12, 4)
        rd = 'r' + str(rd)

        data = proc.readAddr(address, 2)
        data = utils.signExtend(data, 16, 32)

        setattr(proc, rd, data)

class ARMLdrtInstruction(object):
    implements(IARMInstruction)

    testmask = 0b00001101011100000000000000000000
    bitmask  = 0b00000100001100000000000000000000

    def execute(self, proc, inst):
        if not utils.checkCondition(proc, inst):
            return

        modes =  component.getAllUtilitiesRegisteredFor(IARMLSAddressingMode)
        for mode in modes:
            if utils.testInstruction(mode, inst):
                address = mode.getVal(proc, inst)
                break
        rd = utils.getBits(inst, 12, 4)
        rd = 'r' + str(rd)

        data = proc.readAddr(address)

        setattr(proc, rd, data)

class ARMStm1Instruction(object):
    implements(IARMInstruction)

    testmask = 0b00001110010100000000000000000000
    bitmask  = 0b00001000000000000000000000000000

    def execute(self, proc, inst):
        if not utils.checkCondition(proc, inst):
            return

        modes =  component.getAllUtilitiesRegisteredFor(IARMLSMAddressingMode)
        for mode in modes:
            if utils.testInstruction(mode, inst):
                start_address, end_address = mode.getVal(proc, inst)
                break

        register_list = Bitset(utils.getBits(inst, 0, 16), 32)

        address = start_address
  
        for i in range(16):
            if register_list[i]:
                proc.saveAddr(address, getattr(proc, 'r' + str(i)))
                address += 4

        if end_address != address - 4:
            raise exceptions.DataAbort()

class ARMStm2Instruction(object):
    implements(IARMInstruction)

    testmask = 0b00001110011100000000000000000000
    bitmask  = 0b00001000010000000000000000000000

    def execute(self, proc, inst):
        if not utils.checkCondition(proc, inst):
            return

        modes =  component.getAllUtilitiesRegisteredFor(IARMLSMAddressingMode)
        for mode in modes:
            if utils.testInstruction(mode, inst):
                start_address, end_address = mode.getVal(proc, inst)
                break
        print "Ejecutaste un stm(2)"

class ARMStrInstruction(object):
    implements(IARMInstruction)

    testmask = 0b00001100010100000000000000000000
    bitmask  = 0b00000100000000000000000000000000

    def execute(self, proc, inst):
        if not utils.checkCondition(proc, inst):
            return

        modes =  component.getAllUtilitiesRegisteredFor(IARMLSAddressingMode)
        for mode in modes:
            if utils.testInstruction(mode, inst):
                address = mode.getVal(proc, inst)
                break
        rd = utils.getBits(inst, 12, 4)
        rd = 'r' + str(rd)

        proc.saveAddr(address, getattr(proc, rd))


class ARMStrbInstruction(object):
    implements(IARMInstruction)

    testmask = 0b00001100010100000000000000000000
    bitmask  = 0b00000100010000000000000000000000

    def execute(self, proc, inst):
        if not utils.checkCondition(proc, inst):
            return

        modes =  component.getAllUtilitiesRegisteredFor(IARMLSAddressingMode)
        for mode in modes:
            if utils.testInstruction(mode, inst):
                address = mode.getVal(proc, inst)
                break
        rd = utils.getBits(inst, 12, 4)
        rd = 'r' + str(rd)

        value = getattr(proc, rd)
        value = utils.getBits(value, 0, 8)

        proc.saveAddr(address, value, 1)

class ARMStrbtInstruction(object):
    implements(IARMInstruction)

    testmask = 0b00001101011100000000000000000000
    bitmask  = 0b00000100011000000000000000000000

    def execute(self, proc, inst):
        if not utils.checkCondition(proc, inst):
            return

        modes =  component.getAllUtilitiesRegisteredFor(IARMLSAddressingMode)
        for mode in modes:
            if utils.testInstruction(mode, inst):
                address = mode.getVal(proc, inst)
                break
        rd = utils.getBits(inst, 12, 4)
        rd = 'r' + str(rd)

        value = getattr(proc, rd)
        value = utils.getBits(value, 0, 8)

        proc.saveAddr(address, value, 1)

class ARMStrdInstruction(object):
    implements(IARMInstruction)

    testmask = 0b00001110000100000000000011110000
    bitmask  = 0b00000000000000000000000011110000

    def execute(self, proc, inst):
        if not utils.checkCondition(proc, inst):
            return

        modes =  component.getAllUtilitiesRegisteredFor(IARMLSAddressingMode)
        for mode in modes:
            if utils.testInstruction(mode, inst):
                address = mode.getVal(proc, inst)
                break
        rd = utils.getBits(inst, 12, 4)
        rn = rd + 1
        rd = 'r' + str(rd)
        rn = 'r' + str(rn)

        value = getattr(proc, rd)
        proc.saveAddr(address, value)

        value = getattr(proc, rn)
        proc.saveAddr(address + 4, value)

class ARMStrhInstruction(object):
    implements(IARMInstruction)

    testmask = 0b00001110000100000000000011110000
    bitmask  = 0b00000000000000000000000010110000

    def execute(self, proc, inst):
        if not utils.checkCondition(proc, inst):
            return

        modes =  component.getAllUtilitiesRegisteredFor(IARMLSAddressingMode)
        for mode in modes:
            if utils.testInstruction(mode, inst):
                address = mode.getVal(proc, inst)
                break
        rd = utils.getBits(inst, 12, 4)
        rd = 'r' + str(rd)

        value = getattr(proc, rd)
        value = utils.getBits(value, 0, 16)

        proc.saveAddr(address, value, 2)

class ARMStrtInstruction(object):
    implements(IARMInstruction)

    testmask = 0b00001101011100000000000000000000
    bitmask  = 0b00000100001000000000000000000000

    def execute(self, proc, inst):
        if not utils.checkCondition(proc, inst):
            return

        modes =  component.getAllUtilitiesRegisteredFor(IARMLSAddressingMode)
        for mode in modes:
            if utils.testInstruction(mode, inst):
                address = mode.getVal(proc, inst)
                break
        rd = utils.getBits(inst, 12, 4)
        rd = 'r' + str(rd)

        proc.saveAddr(address, getattr(proc, rd))

#Addressing Mode 2 - Load and Store Word or Unsigned Byte
class ARMLSAddressingMode1(object):
    implements(IARMLSAddressingMode)

    testmask = 0b00001111001000000000000000000000
    bitmask  = 0b00000101000000000000000000000000

    def getVal(self, proc, inst):
        u         = utils.getBits(inst, 23)
        rn        = utils.getBits(inst, 16, 4)
        rn        = 'r' + str(rn)
        rnVal     = getattr(proc, rn)
        offset_12 = utils.getBits(inst, 0, 12)
        if u == 1:
            address = rnVal + offset_12
        else:
            address = rnVal - offset_12
        return address


class ARMLSAddressingMode2(object):
    implements(IARMLSAddressingMode)

    testmask = 0b00001111001000000000111111110000
    bitmask  = 0b00000111000000000000000000000000

    def getVal(self, proc, inst):
        u         = utils.getBits(inst, 23)
        rn        = utils.getBits(inst, 16, 4)
        rn        = 'r' + str(rn)
        rnVal     = getattr(proc, rn)
        rm        = utils.getBits(inst, 0, 4)
        rm        = 'r' + str(rm)
        rmVal     = getattr(proc, rm)
        if u == 1:
            address = rnVal + rmVal
        else:
            address = rnVal - rmVal
        return address

class ARMLSAddressingMode3(object):
    implements(IARMLSAddressingMode)

    testmask = 0b00001111001000000000000000010000
    bitmask  = 0b00000111000000000000000000000000

    def getVal(self, proc, inst):
        u         = utils.getBits(inst, 23)
        rn        = utils.getBits(inst, 16, 4)
        rn        = 'r' + str(rn)
        rnVal     = getattr(proc, rn)
        rm        = utils.getBits(inst, 0, 4)
        rm        = 'r' + str(rm)
        rmVal     = getattr(proc, rm)

        shift     = utils.getBits(inst, 5, 2)
        shift_imm = utils.getBits(inst, 7, 5)

        if shift == 0: #LSL
            index = rmVal << shift_imm
            index &= 0xFFFFFFFF
        elif shift == 1: #LSR
            if shift_imm == 0:
                index = 0
            else:
                index = rmVal >> shift_imm
        elif shift == 2: #ASR
            if shift_imm == 0:
                if utils.getBits(rmVal, 31) == 1:
                    index = 0xFFFFFFFF
                else:
                    index = 0
            else:
                index = utils.asr(rmVal, shift_imm)
        elif shift == 3: #ROR or RRX
            if shift_imm == 0:
                index = (proc.statusFlag('C') << 31) | (rmVal >> 1)
            else:
                index = utils.ror(rmVal, 32, shift_imm)

        if u == 1:
            address = rnVal + index
        else:
            address = rnVal - index
        return address

class ARMLSAddressingMode4(object):
    implements(IARMLSAddressingMode)

    testmask = 0b00001111001000000000000000000000
    bitmask  = 0b00000101001000000000000000000000

    def getVal(self, proc, inst):
        u         = utils.getBits(inst, 23)
        rn        = utils.getBits(inst, 16, 4)
        rn        = 'r' + str(rn)
        rnVal     = getattr(proc, rn)
        offset_12 = utils.getBits(inst, 0, 12)
        if u == 1:
            address = rnVal + offset_12
        else:
            address = rnVal - offset_12

        if utils.checkCondition(proc, inst):
            setattr(proc, rn, address)

        return address

class ARMLSAddressingMode5(object):
    implements(IARMLSAddressingMode)

    testmask = 0b00001111001000000000111111110000
    bitmask  = 0b00000111001000000000000000000000

    def getVal(self, proc, inst):
        u         = utils.getBits(inst, 23)
        rn        = utils.getBits(inst, 16, 4)
        rn        = 'r' + str(rn)
        rnVal     = getattr(proc, rn)
        rm        = utils.getBits(inst, 0, 4)
        rm        = 'r' + str(rm)
        rmVal     = getattr(proc, rm)

        if u == 1:
            address = rnVal + rmVal
        else:
            address = rnVal - rmVal

        if utils.checkCondition(proc, inst):
            setattr(proc, rn, address)

        return address

class ARMLSAddressingMode6(object):
    implements(IARMLSAddressingMode)

    testmask = 0b00001111001000000000000000010000
    bitmask  = 0b00000111001000000000000000000000

    def getVal(self, proc, inst):
        u         = utils.getBits(inst, 23)
        rn        = utils.getBits(inst, 16, 4)
        rn        = 'r' + str(rn)
        rnVal     = getattr(proc, rn)
        rm        = utils.getBits(inst, 0, 4)
        rm        = 'r' + str(rm)
        rmVal     = getattr(proc, rm)

        shift     = utils.getBits(inst, 5, 2)
        shift_imm = utils.getBits(inst, 7, 5)

        if shift == 0: #LSL
            index = rmVal << shift_imm
            index &= 0xFFFFFFFF
        elif shift == 1: #LSR
            if shift_imm == 0:
                index = 0
            else:
                index = rmVal >> shift_imm
        elif shift == 2: #ASR
            if shift_imm == 0:
                if utils.getBits(rmVal, 31) == 1:
                    index = 0xFFFFFFFF
                else:
                    index = 0
            else:
                index = utils.asr(rmVal, shift_imm)
        elif shift == 3: #ROR or RRX
            if shift_imm == 0:
                index = (proc.statusFlag('C') << 31) | (rmVal >> 1)
            else:
                index = utils.ror(rmVal, 32, shift_imm)

        if u == 1:
            address = rnVal + index
        else:
            address = rnVal - index

        if utils.checkCondition(proc, inst):
            setattr(proc, rn, address)

        return address

#Load and Store Multiple Addressing modes
class ARMLSMAddressingMode1(object):
    implements(IARMLSMAddressingMode)

    testmask = 0b00001111100000000000000000010000
    bitmask  = 0b00001000100000000000000000000000

    def getVal(self, proc, inst):
        rn = utils.getBits(inst, 16, 4)
        rn = 'r' + str(rn)
        register_list = utils.getBits(inst, 0, 16)
        rnVal = getattr(proc, rn)
        
        start_address = rnVal
        end_address = rnVal + (utils.countSetBits(register_list) * 4) - 4

        if utils.checkCondition(proc, inst):
            setattr(proc, rn, end_address + 4)

        return (start_address, end_address)

class ARMLSMAddressingMode2(object):
    implements(IARMLSMAddressingMode)

    testmask = 0b00001111100000000000000000010000
    bitmask  = 0b00001001100000000000000000000000

    def getVal(self, proc, inst):
        rn = utils.getBits(inst, 16, 4)
        rn = 'r' + str(rn)
        register_list = utils.getBits(inst, 0, 16)
        rnVal = getattr(proc, rn)
        w = utils.getBits(inst, 21)
        
        start_address = rnVal + 4
        end_address = rnVal + (utils.countSetBits(register_list) * 4)

        if utils.checkCondition(proc, inst) and w == 1:
            setattr(proc, rn, end_address)

        return (start_address, end_address)

class ARMLSMAddressingMode3(object):
    implements(IARMLSMAddressingMode)

    testmask = 0b00001111100000000000000000010000
    bitmask  = 0b00001000000000000000000000000000

    def getVal(self, proc, inst):
        rn = utils.getBits(inst, 16, 4)
        rn = 'r' + str(rn)
        register_list = utils.getBits(inst, 0, 16)
        rnVal = getattr(proc, rn)
        w = utils.getBits(inst, 21)
        
        start_address = rnVal - (utils.countSetBits(register_list) * 4) + 4
        end_address = rnVal

        if utils.checkCondition(proc, inst) and w == 1:
            setattr(proc, rn, start_address - 4)

        return (start_address, end_address)

class ARMLSMAddressingMode4(object):
    implements(IARMLSMAddressingMode)

    testmask = 0b00001111100000000000000000010000
    bitmask  = 0b00001001000000000000000000000000

    def getVal(self, proc, inst):
        rn = utils.getBits(inst, 16, 4)
        rn = 'r' + str(rn)
        register_list = utils.getBits(inst, 0, 16)
        rnVal = getattr(proc, rn)
        w = utils.getBits(inst, 21)
        
        start_address = rnVal - (utils.countSetBits(register_list) * 4)
        end_address = rnVal - 4

        if utils.checkCondition(proc, inst) and w == 1:
            setattr(proc, rn, start_address)

        return (start_address, end_address)

