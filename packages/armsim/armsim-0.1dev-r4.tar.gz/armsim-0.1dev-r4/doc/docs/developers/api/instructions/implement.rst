.. armsim contribute file

Implementing a new instruction
==================================

This are the steps required to implement a new instruction.

Most of the instructions are already recognized, to do so 2 fields are 
required in each instruction class, for example the and instruction
(which is in the module: armsim/instruction/dp.py) has the following fields::

    testmask = 0b00001101111000000000000000000000
    bitmask  = 0b00000000000000000000000000000000

The testmask are the bits which need to be checked and the bitmask are those
bits values, the operation executed to check if this is the right instruction
is::

    (instruction & testmask) == bitmask

If this returns true, the execute method is executed.

There are a number of utilities in the armsim.utils package, which you can use
look for examples in the armsim/instruction/dp.py file! (this should be 
documented soon)

