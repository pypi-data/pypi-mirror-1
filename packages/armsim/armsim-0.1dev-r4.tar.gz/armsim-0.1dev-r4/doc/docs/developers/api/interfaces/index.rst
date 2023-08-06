.. armsim contribute file

Interface API
==================================

This are the interfaces, they use zope.interface to be queried.

Instructions and addressing modes are very similar, so only the instruction
interface is documented here.

Interfaces are used to query about which instructions and addressing modes
are available currently

They are registered in the armsim.instruction package's __init__.py, it is
found in armsim/instruction/__init__.py

.. toctree::

    processor
    instruction


