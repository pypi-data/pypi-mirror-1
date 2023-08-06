"""
This is the main simulator module, here the main function is 
contained
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

from armsim.interfaces.armprocessor import IARMProcessor
from armsim.interfaces.arminstruction import IARMInstruction
from armsim.utils import testInstruction
from threading import Thread
from armsim import utils
from zope import component 
from optparse import OptionParser
from code import interact
import sys

class ARMSim(Thread):

    def __init__(self):
        Thread.__init__(self)

    def run(self):
        processor = component.queryUtility(IARMProcessor)
        processor.run()

def init(program, options):
    processor = component.queryUtility(IARMProcessor)
    processor.initMemory(int(options.memory_size))
 
    if options.halt:
        processor.halt()

    i = int(options.load_addr)

    while(True):
        c = program.read(1)
        if c == '':
            break
        processor.memory[i] = ord(c)
        i += 1

    processor.pc = int(options.entry_point)

    program.close()

    run()


def run():
    sim = ARMSim()
    processor = component.queryUtility(IARMProcessor)
    ic_locals = {}
    ic_locals['processor'] = processor
    ic_locals['copyright'] = "Copyright (C) 2009 armsim authors, check the authors in the source AUTHORS file"
    sim.start()
    banner = """armsim Copyright (C) 2009 armsim authors
This program comes with ABSOLUTELY NO WARRANTY.
This program is free software, and you are welcome to redistribute
it under certain conditions, check GPLv3 text for details
             """
    interact(banner, local=ic_locals)



def main():
    usage  = "usage: %prog [options] arm_program"
    parser = OptionParser(usage=usage)
    parser.add_option('-e', '--entry', dest='entry_point', default=0,
                      help='Entry point where te program starts, default 0')
    parser.add_option('-l', '--loadaddr', dest='load_addr', default=0,
                      help='Load addr of the program, default 0')
    parser.add_option('-m', '--memsize', dest='memory_size', default=128*1024,
                      help='Size of memory in bytes, default 131072 (128k)')
    parser.add_option('-H', '--halt', dest='halt', 
                      default=False, action='store_true',
                      help='Dont run the program automatically')
    (options, args) = parser.parse_args()

    if len(args) != 1:
        parser.print_help()
        return
    else:
        try:
            programName = args[0]
            program = open(programName, 'r')
        except IOError:
            print "ARM Program %s does not exist" % programName
            return
    
    init(program, options)

