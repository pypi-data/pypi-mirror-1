.. armsim usage file

Usage
==================================

**WARNING: armsim is still under heavy development, it is a new project and it
still has to implement a lot of the functionality needed in order to use it**

Sample
------

This is a sample of running a test.bin program, just check it!::

    armsim test.bin

After this you'll get a standard python prompt, from here you can
query the processor for it's status or even use it to debug.

There you can use the processor object to get the processor status, get the
processor register values or even change them!

the processor object conforms to the armsim.interfaces.armprocessor.IARMProcessor interface, you can find all of its fields and method here :doc:`/developers/api/interfaces/processor`

For example if we have the following test.s program::

    mov r0, #5
    sub r0, r0, #3

we assemble it and run it, we could do the following::

    armsim test.bin 
    Python 2.6.2 (r262:71600, May  5 2009, 06:32:05) 
    [GCC 4.3.2] on linux2
    Type "help", "copyright", "credits" or "license" for more information.
    (InteractiveConsole)
    >>> processor.r0
    2L
    >>> processor.printStatus()
    processor.printStatus()
    Processor halted execution at 0x8
    r14_und=0
    r13_fiq=0
    spsr_fiq=0
    r15=8
    r12_fiq=0
    r12=0
    r13=0
    r13_abt=0
    r11_fiq=0
    r11=0
    r14_svc=0
    cpsr=211
    r10_fiq=0
    spsr_svc=0
    r13_svc=0
    r9_fiq=0
    spsr_irq=0
    r4=0
    r14=0
    r14_fiq=0
    r14_abt=0
    r10=0
    spsr_abt=0
    r8_fiq=0
    r5=0
    r6=0
    r7=0
    r0=2
    r1=0
    r2=0
    r3=0
    spsr_und=0
    r13_und=0
    r8=0
    r9=0
    r14_irq=0
    r13_irq=0
    >>> processor.pc = 4
    >>> processor.r0 = 10
    >>> processor.resume()
    >>> processor.r0
    7L

This way can debug a program, changing register values in runtime, changing
the program counter and executing again

Generate binary using GCC
-------------------------

This is tested with an ARM GNU toolchain, you can get instructions to build it
here:

`GNU ARM <http://gnuarm.org/support.html>`_

armsim has been tested using gcc generated binary files in binary format, and 
without libc (which really means plain old binary files, no ELF, no A.OUT)

This is the process to produce a binary file from a C program using gcc::

    arm-elf-gcc -c test.c
    arm-elf-ld -e main -nostdlib test.o -o test.out
    arm-elf-objcopy -O binary test.out test.bin

The -e parameter is the name of the function to be called initially

You could also generate the assembly code like this::
  
    arm-elf-gcc -S test.c


This is the process to produce a binary file from an assembly
program using gcc::

    arm-elf-gcc -c test.s
    arm-elf-ld -nostdlib test.o -o test.out
    erm-elf-objcopy -O binary test.out test.bin

And you are done, you have your binary to test with armsim

Options
-------

This are the options that armsim currently accepts::

    Usage: armsim [options] arm_program

    Options:
      -h, --help            show this help message and exit
      -e ENTRY_POINT, --entry=ENTRY_POINT
                            Entry point where te program starts, default 0
      -l LOAD_ADDR, --loadaddr=LOAD_ADDR
                            Load addr of the program, default 0
      -m MEMORY_SIZE, --memsize=MEMORY_SIZE
                            Size of memory in bytes, default 131072 (128k)
      -H, --halt            Dont run the program automatically

* ENTRY_POINT The entry parameter is the instruction that is initially loaded to the pc register of the ARM processor
* LOAD_ADDR   Initial address where input program is going to be stored
* MEMORY_SIZE Processor's memory size
* HALT Processor initializes in halt state




