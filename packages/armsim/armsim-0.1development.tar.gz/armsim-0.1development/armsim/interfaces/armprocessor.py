from zope.interface import Interface
from zope.interface import Attribute

class IARMProcessor(Interface):
    """This interface defines the ARM processor"""

    memory = Attribute("Processor memory buffer")

    r0  = Attribute("R0 register")
    r1  = Attribute("R1 register")
    r2  = Attribute("R2 register")
    r3  = Attribute("R3 register")
    r4  = Attribute("R4 register")
    r5  = Attribute("R5 register")
    r6  = Attribute("R6 register")
    r7  = Attribute("R7 register")
    r8  = Attribute("R8 register")
    r9  = Attribute("R9 register")
    r10 = Attribute("R10 register")
    r11 = Attribute("R11 register")
    r12 = Attribute("R12 register")
    r13 = Attribute("R13 register")
    r14 = Attribute("R14 register, holds SP")
    r15 = Attribute("R15 register, holds PC")

    #Supervisor mode registers
    r13_svc = Attribute("Supervisor mode R13 register")
    r14_svc = Attribute("Supervisor mode R14 register")
    spsr_svc = Attribute("Supervisor mode SPSR status register")

    #Abort mode registers
    r13_abt = Attribute("Abort mode R13 register")
    r14_abt = Attribute("Abort mode R14 register")
    spsr_abt = Attribute("Abort mode SPSR status register")

    #Undefined mode registers
    r13_und = Attribute("Undefined mode R13 register")
    r14_und = Attribute("Undefined mode R14 register")
    spsr_und = Attribute("Undefined mode SPSR status register")

    #IRQ mode registers
    r13_irq = Attribute("IRQ mode R13 register")
    r14_irq = Attribute("IRQ mode R14 register")
    spsr_irq = Attribute("IRQ mode SPSR status register")

    #FIQ mode registers
    r8_fiq = Attribute("FIQ mode R8 register")
    r9_fiq = Attribute("FIQ mode R9 register")
    r10_fiq = Attribute("FIQ mode R10 register")
    r11_fiq = Attribute("FIQ mode R11 register")
    r12_fiq = Attribute("FIQ mode R12 register")
    r13_fiq = Attribute("FIQ mode R13 register")
    r14_fiq = Attribute("FIQ mode R14 register")
    spsr_fiq = Attribute("FIQ mode SPSR status register")

    cpsr = Attribute("CPSR Status register")

    def halt():
        """Pauses execution"""

    def printStatus():
        """Prints execution state, current PC and value of all registers"""

    def initMemory(size):
        """Initializes the memory to the size of the parameter passed"""

    def reset():
        """Resets the processor, CAUTION registers are not erased"""

    def fetch():
        """Looks for the next instruction and returns it"""

    def resume():
        """
           Resumes execution at current PC, you can use this method along with
           halt to debug, and change register values at runtime
           Example: 
                processor.halt()

                processor.r0
                45L
                processor.r0 = 15
                processor.resume()
        """

    def step():
        """
           Jumps to the next instruction, processor automatically executes this
           after a fetch
        """

    def setStatusFlag(flag, value):
        """
           Used to change status flags, values allowed to the flag variable are:
           'M' for mode
           'T' for thumb instruction set (altough this isn't supported)
           'J' for Jazzelle instruction set (it isn't supported yet)

           You can read about the rest of the bits
           in the ARM Architecture Manual
           'F' 
           'I'
           'A'
           'E'
           'GE'
           'Q' 

           and condition code flags:
           'V' oVerflow
           'C' Carry 
           'Z' Zero
           'N' Negative
        """

    def statusFlag(flag):
        """
           Returns the value of a status flag, 
           values allowed to the flag variable are:
           'M' for mode
           'T' for thumb instruction set (altough this isn't supported)
           'J' for Jazzelle instruction set (it isn't supported yet)

           You can read about the rest of the bits
           in the ARM Architecture Manual
           'F' 
           'I'
           'A'
           'E'
           'GE'
           'Q' 

           and condition code flags:
           'V' oVerflow
           'C' Carry 
           'Z' Zero
           'N' Negative
        """

    def mode():
        """Shortcut to statusFlag('M')"""
