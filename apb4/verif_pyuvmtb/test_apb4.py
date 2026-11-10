import cocotb
import pyuvm 
import inspect
from cocotb.triggers import *
from cocotb.clock import Clock
from pyuvm import *
from apb4_tb import *
from apb4_seq import *


class APB4Test(uvm_test):



    def build_phase(self):


         if not hasattr(self, "rsp_delay"):
                    self.rsp_delay = 0
        
         if not hasattr(self, "cmd_delay"):
             self.cmd_delay = 0
         
         if not hasattr(self, "idle"):
             self.idle = 0
         
         if not hasattr(self, "count"):
                self.count = 1
        
         self.env = apb4_env("env",self)
         self.seq  = APB4_Sequence.create("seq")
         self.b_seq = Backend_Seq.create("b_seq")
         self.valid_addr_list = []
         self.seq.count = self.count
         self.b_seq.count = self.count
         for valid_addr in range(0x1000,0x2000):
                        self.valid_addr_list.append(valid_addr)


         ### Configuration setting of various variables
         ConfigDB().set(self,"env.b_agent.b_driver","RSP_DELAY",self.rsp_delay)     
         ConfigDB().set(self,"env.b_agent.b_driver","CMD_DELAY",self.cmd_delay)     
         ConfigDB().set(self,"env.m_agent.m_driver","IDLE",self.idle)     
         ConfigDB().set(self,"env.b_agent.b_driver","ADDR_LIST",self.valid_addr_list)
         ConfigDB().set(self,"env.scoreboard","ADDR_LIST",self.valid_addr_list)
    
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

        self.count = 3
        uvm_factory().set_type_override_by_type(APB4_Sequence,APB4_Write_Seq)
        super().build_phase()

@pyuvm.test()
class t_read_basic(APB4Test):

    def build_phase(self):

    
        uvm_factory().set_type_override_by_type(APB4_Sequence,APB4_Read_Seq)
        super().build_phase()

@pyuvm.test()
class t_pattern_basic(APB4Test):

    def build_phase(self):
        # Replace the default APB sequence with the 32-item pattern sequence.
        uvm_factory().set_type_override_by_type(
            APB4_Sequence, APB4_Pattern_WALK_ONE_ZERO
        )

        # The current backend driver consumes one backend item for every
        # command, so provide 32 backend items for the 32 APB writes.
        uvm_factory().set_type_override_by_type(
            Backend_Seq, Backend_Pattern_Seq
        )

        super().build_phase()


@pyuvm.test()
class t_error_resp(APB4Test):

    def build_phase(self):

        uvm_factory().set_type_override_by_type(APB4_Sequence,APB4_Write_Seq)
        # uvm_factory().set_type_override_by_type(APB4_Sequence,APB4_Read_Seq)
        super().build_phase()


@pyuvm.test()
class t_rsp_delay(APB4Test):

    def build_phase(self):

         
         self.rsp_delay = 4
         uvm_factory().set_type_override_by_type(APB4_Sequence,APB4_Write_Seq)
         super().build_phase()


@pyuvm.test()
class t_cmd_backpressure(APB4Test):

    def build_phase(self):

         
         self.cmd_delay = 18
         uvm_factory().set_type_override_by_type(APB4_Sequence,APB4_Write_Seq)
         super().build_phase()


@pyuvm.test()
class t_back_to_back_write(APB4Test):

    def build_phase(self):

        self.idle = 0
        self.count = 3
        uvm_factory().set_type_override_by_type(APB4_Sequence,APB4_Write_Seq)
        # uvm_factory().set_type_override_by_type(Backend_Sequence,Backend_Seq)
        super().build_phase()

@pyuvm.test()
class t_back_to_back_read(APB4Test):

    def build_phase(self):

        self.idle = 0
        self.count = 3
        uvm_factory().set_type_override_by_type(APB4_Sequence,APB4_Read_Seq)
        uvm_factory().set_type_override_by_type(Backend_Sequence,Backend_Seq)
        super().build_phase()

@pyuvm.test()
class t_rand_mix(APB4Test):

    def build_phase(self):

        self.count = 2


        # uvm_factory().set_type_override_by_type(APB4_Sequence,APB4_Write_Seq)
        uvm_factory().set_type_override_by_type(APB4_Sequence,APB4_Read_Seq)

        super().build_phase()
        self.seq.random_mode = True