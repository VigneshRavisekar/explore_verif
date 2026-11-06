import cocotb
import pyuvm 
from cocotb.triggers import Timer, RisingEdge, FallingEdge,ReadOnly
from cocotb.clock import Clock  
from pyuvm import *
from apb4_master_agent import *
from apb4_backend_agent import *


# async def reset():

        
#         await FallingEdge(cocotb.top.pclk)
#         cocotb.top.presetn.value = 0
#         await Timer(2,"ns")
#         cocotb.top.presetn.value = 1
    


# class apb4_tester(uvm_component):

#     def build_phase(self):

#         self.dut = cocotb.top
#         self.master_bpp = uvm_blocking_put_port("master_bpp", self)
#         self.backend_bpp = uvm_blocking_put_port("backend_bpp", self)

#     def start_of_simulation_phase(self):

#         cocotb.start_soon(Clock(cocotb.top.pclk,2,"ns").start())


#     async def run_phase(self):

#          await reset()
#          packet  = ConfigDB().get(self,"","PACKET")
#          self.logger.info(packet)
#          if packet["write"] == 1:
#             await self.master_bpp.put(packet)
#          else:
#              await self.master_bpp.put(packet)
#              await self.backend_bpp.put(packet)


class Scoreboard(uvm_scoreboard):

     def build_phase(self):

        self.m_mon_fifo = uvm_tlm_analysis_fifo("master_mon_fifo",self)
        self.b_mon_fifo = uvm_tlm_analysis_fifo("b_mon_fifo",self)
        self.m_mon_gp   = uvm_get_port("m_mon_gp",self)
        self.b_mon_gp   = uvm_get_port("b_mon_gp",self)

     def connect_phase(self):

        self.m_mon_gp.connect(self.m_mon_fifo.get_export)
        self.b_mon_gp.connect(self.b_mon_fifo.get_export)

     async def run_phase(self):

         
         self.sent_packet    = await self.m_mon_gp.get()
         self.command_packet = await self.b_mon_gp.get()
    
     def check_phase(self):

        passed = True
        for key in self.sent_packet:
            if self.sent_packet[key] != self.command_packet[key]:
                self.logger.error(
                    f"MISMATCH {key}: apb={self.sent_packet[key]} backend={self.command_packet[key]}")
                passed = False
            else:
                self.logger.info(f"{key} matches: {self.sent_packet[key]}")
        assert passed, "scoreboard found mismatches"
         
    

class apb4_env(uvm_env):

    def build_phase(self):

        self.apb4_seqr    = uvm_sequencer("apb4_seqr",self)
        ConfigDB().set(None,"*","APB4_SEQUENCER",self.apb4_seqr)
        self.m_agent      = master_agent("m_agent",self)
        self.b_agent      = backend_agent("b_agent",self)
        # self.tester       = apb4_tester("tester",self)
        self.scoreboard   = Scoreboard("scoreboard",self)
        # self.master_fifo  = uvm_tlm_fifo("master_fifo",self)
        self.backend_fifo = uvm_tlm_fifo("backend_fifo",self)
    
    def connect_phase(self):

        #  self.tester.master_bpp.connect(self.master_fifo.put_export)
        #  self.m_agent.m_driver.m_driver_gp.connect(self.master_fifo.get_export)
         self.m_agent.m_driver.seq_item_port.connect(self.apb4_seqr.seq_item_export)
        #  self.tester.backend_bpp.connect(self.backend_fifo.put_export)
         self.b_agent.b_driver.b_driver_gp.connect(self.backend_fifo.get_export)
         self.m_agent.m_monitor.m_monitor_ap.connect(self.scoreboard.m_mon_fifo.analysis_export)
         self.b_agent.b_monitor.b_monitor_ap.connect(self.scoreboard.b_mon_fifo.analysis_export)
    
    def end_of_elaboration_phase(self):

        self.logger.info("APB4_ENV")
    