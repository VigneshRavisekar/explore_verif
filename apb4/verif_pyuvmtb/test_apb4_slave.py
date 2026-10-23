# pyUVM TB for apb4_slave
# Currently building step by step from concepts learned from Salemi Book
import cocotb
import pyuvm   
from pyuvm import *
import logging 
import random   
from cocotb.queue import Queue, QueueEmpty
from cocotb.triggers import Timer, RisingEdge, FallingEdge
from cocotb.clock import Clock 
from apb4_slave_bfm import *

logger = logging.getLogger("cocotb.testbench")

async def reset():

        await FallingEdge(cocotb.top.pclk)
        cocotb.top.presetn.value = 0
        await Timer(2,"ns")
        cocotb.top.presetn.value = 1


class BaseTester(uvm_component):

    def build_phase(self):
        self.bfm = apb4_slave_bfm()

    def start_of_simulation_phase(self):
        self.bfm.start_tasks()
        cocotb.start_soon(Clock(cocotb.top.pclk, 2, units="ns").start())

    async def run_phase(self):
        self.raise_objection()
        await reset()
        await self.send_command()
        await self.bfm.master_completion_queue.get()
        self.drop_objection()
            


class WriteTester(BaseTester):


        async def send_command(self):

            
                await self.bfm.send_write_command(self.parent.addr,self.parent.data,self.parent.strb,self.parent.write)


class ReadTester(BaseTester):

 
      async def send_command(self):

            await self.bfm.send_read_command(self.parent.addr,self.parent.read_data,self.parent.write)

class BaseEnv(uvm_env):

           pass
                  
                    

class WriteEnv(BaseEnv):

            def build_phase(self):
                   super().build_phase()
                   self.tester = WriteTester("tester",self)

class ReadEnv(BaseEnv):

            def build_phase(self):
                   super().build_phase()
                   self.tester = ReadTester("tester",self)

@pyuvm.test()
class WriteTest(uvm_test):


    
       def build_phase(self):

              self.env = WriteEnv("env",self)
              self.env.addr = 0x10
              self.env.data = 0x20
              self.env.strb = 0xF
              self.env.write = 1


@pyuvm.test()
class ReadTest(uvm_test):

       def build_phase(self):

              self.env = ReadEnv("env",self)
              self.env.addr = 0x10
              self.env.read_data = 0x20
              self.env.write = 0
            

# class Scoreboard(uvm_component):

    
#       async def extract_phase(self,master,backend,write):

      
      
#           if write == 1:

#               (master_addr,master_data,master_strb) = await master.get()
#               (backend_addr,backend_data,backend_strb) = await backend.get()
#               self.master_command =  (master_addr,master_data,master_strb)
#               self.backend_command  = (backend_addr,backend_data,backend_strb)
#             #   logger.info(f"Master_command:{master_command}")
#             #   logger.info(f"Backend_command:{backend_command}")
#             #   assert master_command == backend_command

#           else:

#               (master_addr,master_data) = await master.get()
#               (backend_addr,backend_data)  = await backend.get()
#               master_command =  (master_addr,master_data)
#               backend_command  = (backend_addr,backend_data)
#             #   logger.info(f"Master_command:{master_command}")
#             #   logger.info(f"Backend_command:{backend_command}")
#             #   assert master_command == backend_command

#       async def check_phase(self):

#                 logger.info(f"Master_command:{self.master_command}")
#                 logger.info(f"Backend_command:{self.backend_command}")
#                 assert self.master_command == self.backend_command
            
    