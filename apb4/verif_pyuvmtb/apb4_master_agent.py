import cocotb
import pyuvm 
from cocotb.triggers import Timer, RisingEdge, FallingEdge,ReadOnly
from cocotb.clock import Clock  
from pyuvm import *

class master_driver(uvm_driver):


    def build_phase(self):

        self.dut = cocotb.top
        # self.m_driver_gp = uvm_blocking_get_port("m_driver_gp",self)
        self.idle = ConfigDB().get(self,"","IDLE")

    def end_of_elaboration_phase(self):

         self.logger.info("MASTER_DRIVER")
      
    async def run_phase(self):


        while True:
            # self.raise_objection()
            # self.packet = await self.m_driver_gp.get()
            self.packet = await self.seq_item_port.get_next_item()
            ### APB Setup Phase
            await RisingEdge(self.dut.pclk)
            self.dut.s_apb_PWRITE.value = self.packet.apb4_write
            self.dut.s_apb_PSEL.value = 1      
            self.dut.s_apb_PENABLE.value = 0   
            self.dut.s_apb_PADDR.value = self.packet.apb4_addr
            # if self.packet["write"] == 1:
            if self.packet.apb4_write == 1:
                self.dut.s_apb_PWDATA.value = self.packet.apb4_data
                self.dut.s_apb_PSTRB.value = self.packet.apb4_strb


            ### APB ACCESS PHASE
            if self.idle > 0:
                for _ in range(self.idle):
                    await RisingEdge(self.dut.pclk)
            else:
                    await RisingEdge(self.dut.pclk)
            self.dut.s_apb_PENABLE.value = 1
            # while self.dut.s_apb_PREADY.value != 1:
            #     await RisingEdge(self.dut.pclk)
            waited = 0
            while self.dut.s_apb_PREADY.value != 1:
                await RisingEdge(self.dut.pclk)
                waited += 1
                assert waited < 1000, "PREADY never arrived (backend not responding?)"  

            self.dut.s_apb_PENABLE.value = 0
            self.dut.s_apb_PSEL.value = 0
            self.seq_item_port.item_done()
            # self.drop_objection()

class master_monitor(uvm_monitor):

    def build_phase(self):

        self.dut = cocotb.top
        self.m_monitor_ap = uvm_analysis_port("m_monitor_ap",self)


    async def run_phase(self):

         
        while True:
            
            await FallingEdge(self.dut.pclk)
            if self.dut.s_apb_PREADY.value == 1 and  self.dut.s_apb_PENABLE.value == 1 and self.dut.s_apb_PSEL.value == 1:
                             if self.dut.s_apb_PWRITE.value == 1:
                                sampled_packet = {"addr":int(self.dut.s_apb_PADDR.value),"data":int(self.dut.s_apb_PWDATA.value),"strb":int(self.dut.s_apb_PSTRB.value)}
                                self.m_monitor_ap.write(sampled_packet)
                                self.m_monitor_ap.write(self.dut.s_apb_PSLVERR.value)
                             else:
                                  read_packet  = {"addr":int(self.dut.s_apb_PADDR.value),"data":int(self.dut.s_apb_PRDATA.value)}
                                  self.m_monitor_ap.write(read_packet)
                                  self.m_monitor_ap.write(self.dut.s_apb_PSLVERR.value)



class master_agent(uvm_agent):

     def build_phase(self):

          self.m_driver  = master_driver("m_driver",self)
          self.m_monitor = master_monitor("m_monitor",self)

     def end_of_elaboration_phase(self):

          self.logger.info("MASTER_AGENT")
          




