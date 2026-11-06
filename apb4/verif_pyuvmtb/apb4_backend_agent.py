import cocotb
import pyuvm 
from cocotb.triggers import Timer, RisingEdge, FallingEdge,ReadOnly
import logging 
from cocotb.clock import Clock  
from pyuvm import *


class backend_driver(uvm_driver):

    def build_phase(self):

         self.dut = cocotb.top
         

    async def run_phase(self):

          
           
           self.dut.cmd_ready.value = 1 ## Backend is available everytime
           while self.dut.cmd_valid.value != 1:
                 await RisingEdge(self.dut.pclk)
           print("HELLO")
           self.dut.rsp_valid.value = 1
         
           while self.dut.rsp_ready.value == 1:
                 await RisingEdge(self.dut.pclk)
           self.dut.rsp_valid.value = 0

class backend_monitor(uvm_monitor):

      def build_phase(self):
            self.dut = cocotb.top
            self.b_monitor_ap = uvm_analysis_port("b_monitor_ap",self)

      async def run_phase(self):

            while True:
                  await FallingEdge(self.dut.pclk)
                  if(self.dut.cmd_valid.value == 1 and self.dut.cmd_ready.value == 1):
                              break
            self.logger.info("BACK")
            cmd_packet = {"addr":int(self.dut.cmd_paddr.value),"data":int(self.dut.cmd_pwdata.value),"strb":int(self.dut.cmd_pstrb.value)}
            self.b_monitor_ap.write(cmd_packet)



class backend_agent(uvm_agent):

      def build_phase(self):

            self.b_driver  = backend_driver("b_driver",self)
            self.b_monitor = backend_monitor("b_monitor",self)