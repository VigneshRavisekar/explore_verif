import cocotb
import pyuvm 
from cocotb.triggers import Timer, RisingEdge, FallingEdge,ReadOnly
import logging 
from cocotb.clock import Clock  
from pyuvm import *


class backend_driver(uvm_driver):

    def build_phase(self):

         self.dut = cocotb.top
      #    self.b_driver_gp = uvm_blocking_get_port("b_driver_gp",self)


    async def run_phase(self):

              self.backend_rsp = await self.seq_item_port.get_next_item()
              self.dut.cmd_ready.value = 1 ## Backend is available everytime
              while self.dut.cmd_valid.value !=1:
                     await RisingEdge(self.dut.pclk)
              if self.dut.cmd_pwrite.value != 1:
                  self.dut.rsp_prdata.value = self.backend_rsp.rsp_data
              self.dut.rsp_valid.value = 1
              while True:
                       if self.dut.rsp_ready !=1:
                              await RisingEdge(self.dut.pclk)
                       break
              self.dut.rsp_valid.value = 0
              self.seq_item_port.item_done()    
                
      #      self.dut.cmd_ready.value = 1 ## Backend is available everytime
      #      while self.dut.cmd_valid.value != 1:
      #            await RisingEdge(self.dut.pclk)

           
      #      if self.dut.cmd_pwrite.value == 0:
      #       #      self.rdata = (await self.b_driver_gp.get())["data"]
      #            self.backend_rsp = await self.seq_item_port.get_next_item()
      #            self.dut.rsp_prdata.value = self.backend_rsp.rsp_data
      #            self.dut.rsp_valid.value = 1
      #            while True:
      #                  if self.dut.rsp_ready !=1:
      #                   await RisingEdge(self.dut.pclk)
      #                  break
      #            self.dut.rsp_valid.value = 0
      #            self.seq_item_port.item_done()    
      #      else:
      #       while self.dut.rsp_ready.value != 1:
      #            await RisingEdge(self.dut.pclk)
      #       self.dut.rsp_valid.value = 0

class backend_monitor(uvm_monitor):

      def build_phase(self):
            self.dut = cocotb.top
            self.b_monitor_ap = uvm_analysis_port("b_monitor_ap",self)

      async def run_phase(self):

            while True:
                  await FallingEdge(self.dut.pclk)
                  if(self.dut.cmd_valid.value == 1 and self.dut.cmd_ready.value == 1):
                              break
            if self.dut.cmd_pwrite.value == 1:
                  cmd_packet = {"addr":int(self.dut.cmd_paddr.value),"data":int(self.dut.cmd_pwdata.value),"strb":int(self.dut.cmd_pstrb.value)}
                  self.b_monitor_ap.write(cmd_packet)
            else:
                  self.addr = int(self.dut.cmd_paddr.value)
                  while self.dut.rsp_valid.value != 1 or self.dut.rsp_ready.value != 1:
                              await FallingEdge(self.dut.pclk)
                              
                 
                  self.read_data = int(self.dut.rsp_prdata.value)
                  read_packet = {"addr":self.addr,"data":self.read_data}
                  self.b_monitor_ap.write(read_packet)


class backend_agent(uvm_agent):

      def build_phase(self):

            self.b_driver  = backend_driver("b_driver",self)
            self.b_monitor = backend_monitor("b_monitor",self)

      def end_of_elaboration_phase(self):

          self.logger.info("BACKEND_AGENT")