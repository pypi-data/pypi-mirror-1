from zope import component

class _ProcessorMode(object):
    User       = 0b10000
    FIQ        = 0b10001
    IRQ        = 0b10010
    Supervisor = 0b10011
    Abort      = 0b10111
    Undefined  = 0b11011
    System     = 0b11111

    def __setattr__(self, name, val):
        print 'Hola'
        raise AttributeException('Cannot set attribute ' + name)

ProcessorMode = _ProcessorMode()

from armsim.processor.arm9processor import ARM9Processor
from armsim.interfaces.armprocessor import IARMProcessor

component.provideUtility(ARM9Processor())

