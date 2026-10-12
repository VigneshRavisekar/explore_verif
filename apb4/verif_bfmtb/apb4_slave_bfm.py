import cocotb
import pyuvm    
import random   
from cocotb.queue import Queue, QueueEmpty
from cocotb.triggers import Timer, RisingEdge, FallingEdge,ReadOnly
from cocotb.clock import Clock  

class apb4_slave_bfm(metaclass=pyuvm.Singleton):
    def __init__(self):
        self.dut = cocotb.top
        self.master_driver_queue =   Queue()
        self.backend_driver_queue =  Queue()
        self.master_monitor_queue =  Queue()
        self.backend_monitor_queue = Queue()

    async def reset(self):

        await FallingEdge(self.dut.pclk)
        self.dut.presetn.value = 0
        await Timer(2,"ns")
        self.dut.presetn.value = 1

    async def master_driver(self):
        """Master_2_ap4_Driver"""

        while True:

                (addr,data,strb,write) = await self.master_driver_queue.get()

                if write == 1:
                    ## Setup Phase
                    await RisingEdge(self.dut.pclk)
                    self.dut._log.info("Write Operation is Initiated")
                    self.dut.s_apb_PWRITE.value = write
                    self.dut.s_apb_PSEL.value = 1
                    self.dut.s_apb_PENABLE.value = 0
                    self.dut.s_apb_PADDR.value = addr
                    self.dut.s_apb_PWDATA.value = data
                    self.dut.s_apb_PSTRB.value = strb
                    

                    ## Access Phase
                    await RisingEdge(self.dut.pclk)
                    self.dut.s_apb_PENABLE.value = 1
                    while self.dut.s_apb_PREADY.value != 1:
                        await RisingEdge(self.dut.pclk)
                    self.dut.s_apb_PENABLE.value = 0
                    self.dut.s_apb_PSEL.value = 0
                   

                else:
                     ## Setup Phase
                     await RisingEdge(self.dut.pclk)
                     self.dut._log.info("Read Operation is Initiated")
                     self.dut.s_apb_PWRITE.value = write
                     self.dut.s_apb_PSEL.value = 1
                     self.dut.s_apb_PENABLE.value = 0
                     self.dut.s_apb_PADDR.value = addr
                     ## Access Phase
                     await RisingEdge(self.dut.pclk)
                     self.dut.s_apb_PENABLE.value = 1
                     while self.dut.s_apb_PREADY.value != 1:
                         await RisingEdge(self.dut.pclk)
                     self.dut.s_apb_PENABLE.value = 0
                     self.dut.s_apb_PSEL.value = 0
                    

                 
    async def backend_driver(self):
         """Backend_2_apb4_Driver"""
         self.dut.cmd_ready.value = 1 ## Always asserted so that backend always ready to accept the command 
         while self.dut.cmd_valid.value != 1:
              await RisingEdge(self.dut.pclk)
         self.dut._log.info("Command Accepted !!!")
         self.dut.rsp_valid.value = 1
         if self.dut.cmd_pwrite.value == 0:
              rd_data = await self.backend_driver_queue.get()
            #   await RisingEdge(self.dut.pclk)
              self.dut.rsp_prdata.value = rd_data
         while True:
              await RisingEdge(self.dut.pclk)
              if self.dut.rsp_ready.value == 1:
                   self.dut.rsp_valid.value = 0

    async def master_monitor(self):
         """Master Monitor"""
         while True:
              await RisingEdge(self.dut.pclk)
              await ReadOnly()
              if self.dut.s_apb_PWRITE.value == 1:
                    if self.dut.s_apb_PENABLE.value == 1 and self.dut.s_apb_PSEL.value == 1 and self.dut.s_apb_PREADY.value == 1:
                         [addr,data,strb] = [int(self.dut.s_apb_PADDR.value),int(self.dut.s_apb_PWDATA.value),int(self.dut.s_apb_PSTRB.value)]
                         command = [addr,data,strb]
                         await self.master_monitor_queue.put(command)
                         self.dut._log.info(f"Master queue: {self.master_monitor_queue._queue}")
                         self.dut._log.info("Write Operation Completed")
                    
              else:
                    if self.dut.s_apb_PENABLE.value == 1 and self.dut.s_apb_PSEL.value == 1 and self.dut.s_apb_PREADY.value == 1:
                                            read_data = self.dut.s_apb_PRDATA.value
                                            read_command = [int(self.dut.s_apb_PADDR.value),int(read_data)]
                                            await self.master_monitor_queue.put(read_command)
                                            self.dut._log.info(f"Master queue: {self.master_monitor_queue._queue}")
                                            self.dut._log.info("Read Operation Completed")


    async def backend_monitor(self):
          """Backend Monitor"""
          backend_mon = []
          while True:
                await RisingEdge(self.dut.pclk)
                await ReadOnly()
                if self.dut.cmd_valid.value == 1 and self.dut.cmd_ready.value == 1:
                     if self.dut.cmd_pwrite.value == 1:
                           backend_mon.append(int(self.dut.cmd_paddr.value))
                           backend_mon.append(int(self.dut.cmd_pwdata.value))
                           backend_mon.append(int(self.dut.cmd_pstrb.value))
                           print(backend_mon)
                            
                     else:
                           backend_mon.append(int(self.dut.cmd_paddr.value))
                           while True: 
                            await RisingEdge(self.dut.pclk)
                            if self.dut.rsp_valid.value == 1 and self.dut.rsp_ready.value == 1:
                                backend_mon.append(int(self.dut.rsp_prdata.value))
                                break

                if self.dut.rsp_valid.value == 1 and self.dut.rsp_ready.value == 1:
                        
                        await self.backend_monitor_queue.put(backend_mon) 
                        self.dut._log.info(f"Backend queue: {self.backend_monitor_queue._queue}")
                   
              

                      
                        
    def start_tasks(self):
        cocotb.start_soon(self.master_driver()) 
        cocotb.start_soon(self.backend_driver())
        cocotb.start_soon(self.master_monitor())
        cocotb.start_soon(self.backend_monitor())

    async def send_write_command(self,addr,data,strb,write):
        command = (addr,data,strb,write)
        await self.master_driver_queue.put(command)

    async def send_read_command(self,addr,read_data,write):
         command = (addr,False,False,write)
         await self.master_driver_queue.put(command)
         await self.backend_driver_queue.put(read_data)
         
        

