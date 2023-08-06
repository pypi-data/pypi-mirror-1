"""
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

