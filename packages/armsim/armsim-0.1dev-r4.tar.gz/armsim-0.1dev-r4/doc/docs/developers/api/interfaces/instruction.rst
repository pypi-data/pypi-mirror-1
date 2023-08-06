.. armsim api index file

ARM Instruction
==================================

This is the ARM instruction interface, every new instruction must implement
this interface.

Instructions are contained in the armsim.instruction package.

There we have the following modules:

* dp.py Data Processing instructions
* branch.py Branch instructions
* ldstr.py Memory load and store instructions
* mult.py Multiplication instructions
* semaphore.py Semaphore instructions
* status.py Status Register operation instructions
* exception.py Exception generating instructions
* miscellaneous.py Miscellaneous instructions

Most of the instructions are recognized, but it is yet needed to implement most
of this instructions, if you would like to help check the :doc:`/developers/contribute` page

.. autointerface:: armsim.interfaces.arminstruction.IARMInstruction

