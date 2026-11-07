import cocotb
import pyuvm 
from cocotb.triggers import *
from cocotb.clock import Clock
from pyuvm import *
from apb4_tb import *
from apb4_seq import *

class APB4Test(uvm_test):

    def build_phase(self):

        self.env = apb4_env("env",self)
        self.seq  = APB4_Sequence.create("seq")
        self.b_seq = Backend_Seq.create("b_seq")
    
    async def reset(self):

        
        await FallingEdge(cocotb.top.pclk)
        cocotb.top.presetn.value = 0
        await Timer(2,"ns")
        cocotb.top.presetn.value = 1
    
    
    def end_of_elaboration_phase(self):

        self.apb4_seqr = ConfigDB().get(self,"","APB4_SEQUENCER")
        self.backend_seqr = ConfigDB().get(self,"","BACKEND_SEQUENCER")

    def start_of_simulation_phase(self):

        cocotb.start_soon(Clock(cocotb.top.pclk,2,"ns").start())
        

    async def run_phase(self):

        self.raise_objection()
        await self.reset()
        await gather(cocotb.start_soon(self.seq.start(self.apb4_seqr)),cocotb.start_soon(self.b_seq.start(self.backend_seqr)))
        # await Timer(100,"ns")
        self.drop_objection()

@pyuvm.test()
class t_write_basic(APB4Test):

    def build_phase(self):

        uvm_factory().set_type_override_by_type(APB4_Sequence,APB4_Write_Seq)
        super().build_phase()

@pyuvm.test()
class t_read_basic(APB4Test):

    def build_phase(self):

        uvm_factory().set_type_override_by_type(APB4_Sequence,APB4_Read_Seq)
        super().build_phase()



# @pyuvm.test()
# class t_write_basic(uvm_test):

#     def build_phase(self):

#         ## Write_Packet
#         self.addr      = 0x10
#         self.data      = 0x20
#         self.strb      = 0x3
#         self.write     = 1
#         write_packet = {"addr":self.addr,"data":self.data,"strb":self.strb,"write":self.write}
#         self.env  = apb4_env("env",self)
#         ConfigDB().set(self,"env.tester","PACKET",write_packet)


# @pyuvm.test()
# class t_read_basic(uvm_test):

#     def build_phase(self):

#         ### Read_Packet 
#         self.addr       = 0x10
#         self.read_data = 0x20
#         self.write     = 0
#         read_packet = {"addr":self.addr,"data":self.read_data,"write":self.write}
#         self.env  = apb4_env("env",self)
#         ConfigDB().set(self,"env.tester","PACKET",read_packet)