from zope.component import provideUtility
from armsim.interfaces.arminstruction import IARMInstruction
from armsim.interfaces.arminstruction import IARMDPAddressingMode
from armsim.interfaces.arminstruction import IARMLSAddressingMode
from armsim.interfaces.arminstruction import IARMLSMAddressingMode
import dp
import branch
import mult
import miscellaneous
import status
import ldstr
import semaphore
import exception

#Coprocessor instructions

#Multiply instructions
provideUtility(mult.ARMMlaInstruction(), IARMInstruction, 'mla')
provideUtility(mult.ARMMulInstruction(), IARMInstruction, 'mul')
provideUtility(mult.ARMSmlaInstruction(), IARMInstruction, 'smla')
provideUtility(mult.ARMSmlalInstruction(), IARMInstruction, 'smlal')
provideUtility(mult.ARMSmlalxyInstruction(), IARMInstruction, 'smlal<x><y>')
provideUtility(mult.ARMSmlawyInstruction(), IARMInstruction, 'smlaw<y>')
provideUtility(mult.ARMSmullInstruction(), IARMInstruction, 'smull')
provideUtility(mult.ARMSmulwyInstruction(), IARMInstruction, 'smulw<y>')
provideUtility(mult.ARMSmulxyInstruction(), IARMInstruction, 'smul<x><y>')
provideUtility(mult.ARMUmlalInstruction(), IARMInstruction, 'umlal')
provideUtility(mult.ARMUmullInstruction(), IARMInstruction, 'umull')

#Miscellaneous arithmetic instructions
provideUtility(miscellaneous.ARMClzInstruction(), IARMInstruction, 'clz')

#Semaphore instructions
provideUtility(semaphore.ARMSwpInstruction(), IARMInstruction, 'swp')
provideUtility(semaphore.ARMSwpbInstruction(), IARMInstruction, 'swpb')

#Status register access instructions
provideUtility(status.ARMMrsInstruction(), IARMInstruction, 'mrs')
provideUtility(status.ARMMsrInstruction(), IARMInstruction, 'msr')
provideUtility(status.ARMMsriInstruction(), IARMInstruction, 'msri')

#Branch instructions
provideUtility(branch.ARMBlInstruction(), IARMInstruction, 'bl')
provideUtility(branch.ARMBxInstruction(), IARMInstruction, 'bx')
provideUtility(branch.ARMBlx1Instruction(), IARMInstruction, 'blx1')
provideUtility(branch.ARMBlx2Instruction(), IARMInstruction, 'blx2')

#Load and store instructions
provideUtility(ldstr.ARMLdrtInstruction(), IARMInstruction, 'ldrt')
provideUtility(ldstr.ARMLdrInstruction(), IARMInstruction, 'ldr')
provideUtility(ldstr.ARMLdrbtInstruction(), IARMInstruction, 'ldrbt')
provideUtility(ldstr.ARMLdrbInstruction(), IARMInstruction, 'ldrb')
provideUtility(ldstr.ARMLdrdInstruction(), IARMInstruction, 'ldrd')
provideUtility(ldstr.ARMLdrhInstruction(), IARMInstruction, 'ldrh')
provideUtility(ldstr.ARMLdrsbInstruction(), IARMInstruction, 'ldrsb')
provideUtility(ldstr.ARMLdrshInstruction(), IARMInstruction, 'ldrsh')
provideUtility(ldstr.ARMLdm1Instruction(), IARMInstruction, 'ldm1')
provideUtility(ldstr.ARMLdm2Instruction(), IARMInstruction, 'ldm2')
provideUtility(ldstr.ARMStrtInstruction(), IARMInstruction, 'strt')
provideUtility(ldstr.ARMStrInstruction(), IARMInstruction, 'str')
provideUtility(ldstr.ARMStrbtInstruction(), IARMInstruction, 'strbt')
provideUtility(ldstr.ARMStrbInstruction(), IARMInstruction, 'strb')
provideUtility(ldstr.ARMStrdInstruction(), IARMInstruction, 'strd')
provideUtility(ldstr.ARMStrhInstruction(), IARMInstruction, 'strh')
provideUtility(ldstr.ARMStm1Instruction(), IARMInstruction, 'stm1')
provideUtility(ldstr.ARMStm2Instruction(), IARMInstruction, 'stm2')

#Data processing instructions 16 instructions
provideUtility(dp.ARMAndInstruction(), IARMInstruction, 'and')
provideUtility(dp.ARMEorInstruction(), IARMInstruction, 'eor')
provideUtility(dp.ARMSubInstruction(), IARMInstruction, 'sub')
provideUtility(dp.ARMRsbInstruction(), IARMInstruction, 'rsb')
provideUtility(dp.ARMAddInstruction(), IARMInstruction, 'add')
provideUtility(dp.ARMAdcInstruction(), IARMInstruction, 'adc')
provideUtility(dp.ARMSbcInstruction(), IARMInstruction, 'sbc')
provideUtility(dp.ARMRscInstruction(), IARMInstruction, 'rsc')
provideUtility(dp.ARMTstInstruction(), IARMInstruction, 'tst')
provideUtility(dp.ARMTeqInstruction(), IARMInstruction, 'teq')
provideUtility(dp.ARMCmpInstruction(), IARMInstruction, 'cmp')
provideUtility(dp.ARMCmnInstruction(), IARMInstruction, 'cmn')
provideUtility(dp.ARMOrrInstruction(), IARMInstruction, 'orr')
provideUtility(dp.ARMMovInstruction(), IARMInstruction, 'mov')
provideUtility(dp.ARMBicInstruction(), IARMInstruction, 'bic')
provideUtility(dp.ARMMvnInstruction(), IARMInstruction, 'mvn')

#Exception-generating instructions
provideUtility(exception.ARMBkptInstruction(), IARMInstruction, 'bkpt')
provideUtility(exception.ARMSwiInstruction(), IARMInstruction, 'swi')

#DataProcessing addressing modes
provideUtility(dp.ARMDPAddressingMode1(), IARMDPAddressingMode, 'adp1')
provideUtility(dp.ARMDPAddressingMode2(), IARMDPAddressingMode, 'adp2')
provideUtility(dp.ARMDPAddressingMode3(), IARMDPAddressingMode, 'adp3')
provideUtility(dp.ARMDPAddressingMode4(), IARMDPAddressingMode, 'adp4')
provideUtility(dp.ARMDPAddressingMode5(), IARMDPAddressingMode, 'adp5')
provideUtility(dp.ARMDPAddressingMode6(), IARMDPAddressingMode, 'adp6')
provideUtility(dp.ARMDPAddressingMode7(), IARMDPAddressingMode, 'adp7')
provideUtility(dp.ARMDPAddressingMode8(), IARMDPAddressingMode, 'adp8')
provideUtility(dp.ARMDPAddressingMode9(), IARMDPAddressingMode, 'adp9')
provideUtility(dp.ARMDPAddressingMode10(), IARMDPAddressingMode, 'adp10')

#Load Store word or byte addressing modes
provideUtility(ldstr.ARMLSAddressingMode1(), IARMLSAddressingMode, 'als1')
provideUtility(ldstr.ARMLSAddressingMode2(), IARMLSAddressingMode, 'als2')
provideUtility(ldstr.ARMLSAddressingMode3(), IARMLSAddressingMode, 'als3')
provideUtility(ldstr.ARMLSAddressingMode4(), IARMLSAddressingMode, 'als4')
provideUtility(ldstr.ARMLSAddressingMode5(), IARMLSAddressingMode, 'als5')
provideUtility(ldstr.ARMLSAddressingMode6(), IARMLSAddressingMode, 'als6')

#Load Store Multiple word or byte addressing modes
provideUtility(ldstr.ARMLSMAddressingMode1(), IARMLSMAddressingMode, 'alsm1')
provideUtility(ldstr.ARMLSMAddressingMode2(), IARMLSMAddressingMode, 'alsm2')
provideUtility(ldstr.ARMLSMAddressingMode3(), IARMLSMAddressingMode, 'alsm3')
provideUtility(ldstr.ARMLSMAddressingMode4(), IARMLSMAddressingMode, 'alsm4')
