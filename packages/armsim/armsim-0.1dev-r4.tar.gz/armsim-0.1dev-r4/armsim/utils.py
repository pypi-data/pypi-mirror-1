"""
utils.py

created by Eduardo Diaz

This module defines all the common utils needed in order to
make programming the microcontoller easier
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

from armsim.bitset import Bitset

def getBits(num, bit, num_bits=1, size=32):
    """
    Returns the value of a bit or multiple bits of num.

    Example::
        
        num = 0b10001101
        getBits(num, 0)    # returns 1
        getBits(num, 1)    # returns 0
        getBits(num, 4, 4) # returns 8 (0b1000)
        getBits(num, 0, 8) # returns 141 (0b10001101)

    """
    bs = Bitset(num, size)
    if num_bits == 1:
        return int(bs[bit])
    elif num_bits > 1:
        return bitsetRangeToNum(bs[bit:bit+num_bits])
    return 0

def setBits(num, bit, value, num_bits=1, size=32):
    """
    Sets and returns the value of a bit or multiple bits of num.

    Example::
        
        num = 0b10001101 (141)
        setBits(num, 0, 0)    # returns 140 (0b10001100)
        setBits(num, 1, 1)    # returns 143 (0b10001111)
        setBits(num, 4, 5, 4) # returns 221 (0b11011101)

    """
    bs = Bitset(num, size)
    if num_bits == 1:
        bs[bit] = value
    elif num_bits > 1:
        helper = Bitset(value)
        bs[bit:bit+num_bits] = helper[:]
    return int(bs)

def signValue(num, bits=32):
    """
    Returns signed value of num.

    if msb equals zero, it returns num.

    if msb equals one, it returns negative two's complement of num.
    """

    if getBits(num, bits - 1) == 0:
        return num
    else:
        bs = Bitset(num, bits)
        sc = Bitset(1, bits)
        bs = ~bs
        bs, carry = bs + sc
        return -1 * int(bs)

def signExtend(num, bits, newBits):
    """
    Extends a number from *bits* bits to *newBits* bits

    Example::

        num = 0b0011
        signExtend(num, 4, 10) # returns 0b0000000011
        num = 0b1011
        signExtend(num, 4, 10) # returns 0b1111111011

    """
    bs = Bitset(num, newBits)
    bs[bits:newBits] = bs[bits - 1]

    return int(bs)


def testInstruction(inst, inst_val):
    """
    Function to check if an instruction matches the interface's bitmask


    """
    return (inst_val & inst.testmask) == inst.bitmask

def checkCondition(processor, inst_val):
    """
    Checks if an instruction should be executed according to first 4 bits
    of the instruction
    """
    cond = (inst_val & 0xf0000000) >> 28
    if cond == 0:   #EQ
        return processor.statusFlag('Z') == 1
    elif cond == 1: #NE
        return processor.statusFlag('Z') == 0
    elif cond == 2: #CS/HS
        return processor.statusFlag('C') == 1
    elif cond == 3: #CC/LO
        return processor.statusFlag('C') == 0
    elif cond == 4: #MI
        return processor.statusFlag('N') == 1
    elif cond == 5: #PL
        return processor.statusFlag('N') == 0
    elif cond == 6: #VS
        return processor.statusFlag('V') == 1
    elif cond == 7: #VC
        return processor.statusFlag('V') == 0
    elif cond == 8: #HI
        return (processor.statusFlag('C') == 1) and \
               (processor.statusFlag('Z') == 0)
    elif cond == 9: #LS
        return (processor.statusFlag('C') == 0) or \
               (processor.statusFlag('Z') == 1)
    elif cond == 10: #GE
        return processor.statusFlag('N') == processor.statusFlag('V')
    elif cond == 11: #LT
        return processor.statusFlag('N') != processor.statusFlag('V')
    elif cond == 12: #GT
        return (processor.statusFlag('Z') == 0) and \
               (processor.statusFlag('N') == processor.statusFlag('V'))
    elif cond == 13: #LE
        return (processor.statusFlag('Z') == 1) or \
               (processor.statusFlag('N') != processor.statusFlag('V'))
    elif cond == 14: #AL
        return True


def itoa(x, base=10):
    """
        Converts and integer value to its string representation in base *base*


    """
    isNegative = x < 0
    if isNegative:
        x = -x
    digits = []
    while x > 0:
        x, lastDigit = divmod(x, base)
        digits.append('0123456789abcdefghijklmnopqrstuvwxyz'[lastDigit])
    if isNegative:
        digits.append('-')
    digits.reverse()
    return ''.join(digits)

def bitsetRangeToNum(bitset):
    """
    Returns a bitset range converted to a number

    Usage::

        bitsetRangeToNum(bitset[5:8])

    """
    result = 0
    i = 0
    for x in bitset[:]:
        result |= (int(x) << i)
        i += 1
    return result

def ror(val, n, x):
    """
    Executes a rotate right of *x* bits on number *val*, of *n* bits length

    """

    a = val
    b = a >> x
    c = a << (n - x)
    c = c & 0xffffffff
    d = b | c
    return d

def rol(val, n, x):
    """
    Executes a rotate left of *x* bits on number *val*, of *n* bits length

    """
    a = val
    b = a << x
    b = b & 0xffffffff
    c = a >> (n - x)
    d = b | c
    return d

def asr(val, x, n=32):
    """
    Executes an arithmetic shift right of *x* bits on number *val*, of *n* 
    bits length

    """
    msb = getBits(val, n - 1)
    result = val >> x
    result = setBits(result, n - 1, msb)
    return result

def countSetBits(num):
    """
    Returns number of bits set to one

    Example::
 
        countSetBits(5) #returns 2 (0b0101), 2 bits set to 1
        countSetBits(1) #returns 1 (0b0001), 1 bit set to 1

    """
    set = Bitset(num)
    result = 0
    for n in set:
        if n:
            result += 1
    return result


