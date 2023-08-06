from armsim.bitset import Bitset

def getBits(num, bit, num_bits=1, size=32):
    bs = Bitset(num, size)
    if num_bits == 1:
        return int(bs[bit])
    elif num_bits > 1:
        return bitsetRangeToNum(bs[bit:bit+num_bits])
    return 0

def setBits(num, bit, value, num_bits=1, size=32):
    bs = Bitset(num, size)
    if num_bits == 1:
        bs[bit] = value
    elif num_bits > 1:
        helper = Bitset(value)
        bs[bit:bit+num_bits] = helper[:]
    return int(bs)

def signValue(num, bits=32):
    if getBits(num, bits - 1) == 0:
        return num
    else:
        bs = Bitset(num, bits)
        sc = Bitset(1, bits)
        bs = ~bs
        bs, carry = bs + sc
        return -1 * int(bs)

def signExtend(num, bits, newBits):
    bs = Bitset(num, newBits)
    bs[bits:newBits] = bs[bits - 1]

    return int(bs)


def testInstruction(inst, inst_val):
    return (inst_val & inst.testmask) == inst.bitmask

def checkCondition(processor, inst_val):
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
    result = 0
    i = 0
    for x in bitset[:]:
        result |= (int(x) << i)
        i += 1
    return result

def ror(val, n, x):
    a = val
    b = a >> x
    c = a << (n - x)
    c = c & 0xffffffff
    d = b | c
    return d

def rol(val, n, x):
    a = val
    b = a << x
    b = b & 0xffffffff
    c = a >> (n - x)
    d = b | c
    return d

def asr(val, x, n=32):
    msb = getBits(val, n - 1)
    result = val >> x
    result = setBits(result, n - 1, msb)
    return result

def countSetBits(num):
    set = Bitset(num)
    result = 0
    for n in set:
        if n:
            result += 1
    return result


