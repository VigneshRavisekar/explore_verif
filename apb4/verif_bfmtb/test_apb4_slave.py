# APB4 BFM-based verification testbench
# Implementation will be built from the TinyALU BFM concepts.
import cocotb
import pyuvm    
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



async def compare_block(master,backend,write):

    
    
    if write == 1:

        (master_addr,master_data,master_strb) = await master.get()
        (backend_addr,backend_data,backend_strb) = await backend.get()
        master_command =  (master_addr,master_data,master_strb)
        backend_command  = (backend_addr,backend_data,backend_strb)
        logger.info(f"Master_command:{master_command}")
        logger.info(f"Backend_command:{backend_command}")
        assert master_command == backend_command

    else:

        (master_addr,master_data) = await master.get()
        (backend_addr,backend_data)  = await backend.get()
        master_command =  (master_addr,master_data)
        backend_command  = (backend_addr,backend_data)
        logger.info(f"Master_command:{master_command}")
        logger.info(f"Backend_command:{backend_command}")
        assert master_command == backend_command

    

class BaseTester():

    def __init__(self):

            self.bfm = apb4_slave_bfm()


    async def send_command(self):

          pass
    
    
    async def execute(self):

            # await self.bfm.reset()
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


      cocotb.start_soon(Clock(cocotb.top.pclk,2,"ns").start())
      await reset()
      transaction_count = 1
      for _ in range(transaction_count):
            addr = random.randint(0x100,0x200)
            data = random.randint(0x300,0x400)
            strb = 0xF
            write = 0x1
            write_tester = WriteTester(addr,data,strb,write)
            await write_tester.execute()


@cocotb.test()
async def read_test(_):

      cocotb.start_soon(Clock(cocotb.top.pclk,2,"ns").start())
      await reset()
      transaction_count = 1
      for _ in range(transaction_count):
            addr = random.randint(0x100,0x200)
            data = random.randint(0x300,0x400)
            write = 0
            read_tester = ReadTester(addr,data,write)
            await read_tester.execute()
