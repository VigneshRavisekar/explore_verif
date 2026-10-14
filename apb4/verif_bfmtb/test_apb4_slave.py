# APB4 BFM-based verification testbench
# Implementation will be built from the TinyALU BFM concepts.
import cocotb
import pyuvm    
import random   
from cocotb.queue import Queue, QueueEmpty
from cocotb.triggers import Timer, RisingEdge, FallingEdge
from cocotb.clock import Clock 
from verif_bfmtb.apb4_slave_bfm import *

async def compare_block(master,backend,write):

    
    
    if write == 1:
        (master_addr,master_data,master_strb) = await master.get()
        (backend_addr,backend_data,backend_strb) = await backend.get()
        master_command =  (master_addr,master_data,master_strb)
        backed_command  = (backend_addr,backend_data,backend_strb)
        print(master_command)
        print(backed_command)
        assert master_command == backed_command
    else:
        (master_addr,master_data) = await master.get()
        (backend_addr,backend_data)  = await backend.get()
        master_command =  (master_addr,master_data)
        backed_command  = (backend_addr,backend_data)
        print(master_command)
        print(backed_command)
        assert master_command == backed_command

    

class BaseTester():

    def __init__(self):

            self.bfm = apb4_slave_bfm()


    def clock_setup(self):

         cocotb.start_soon(Clock(cocotb.top.pclk,2,"ns").start())

    async def send_command(self):

          pass
    
    
    async def execute(self):

            self.clock_setup()
            await self.bfm.reset()
            self.bfm.start_tasks()
            await self.send_command()
            await compare_block(self.bfm.master_monitor_queue,self.bfm.backend_monitor_queue,self.write)
            await self.bfm.master_completion_queue.get()
            
            


class WriteTester(BaseTester):

        def __init__(self,addr,data,strb,write):
             super().__init__()
             self.addr = addr
             self.data = data
             self.strb = strb
             self.write = write
             

        async def send_command(self):

                await self.bfm.send_write_command(self.addr,self.data,self.strb,self.write)


class ReadTester(BaseTester):

      def __init__(self,addr,read_data,write):
            super().__init__()
            self.addr = addr
            self.read_data = read_data
            self.write = write

      async def send_command(self):

            await self.bfm.send_read_command(self.addr,self.read_data,self.write)


@cocotb.test()
async def write_test(_):

      
      addr = 0x10
      data = 0x20
      strb = 0xF
      write = 0x1
      write_tester = WriteTester(addr,data,strb,write)
      await write_tester.execute()


@cocotb.test()
async def read_test(_):

      addr = 0x10
      data = 0x20
      write = 0
      read_tester = ReadTester(addr,data,write)
      await read_tester.execute()
