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

    




@cocotb.test()
async def basic_write_test(_):
    cocotb.start_soon(Clock(cocotb.top.pclk,2,unit="ns").start())
    bfm = apb4_slave_bfm()
    await bfm.reset()
    bfm.start_tasks()
    addr = 0x1004
    strb = 0xF
    data = 0xFACD
    write = 1
    await bfm.send_write_command(addr,data,strb,write)
    await compare_block(bfm.master_monitor_queue,bfm.backend_monitor_queue,write)   
    # await Timer(100,"ns")


@cocotb.test()
async def basic_read_test(_):
    cocotb.start_soon(Clock(cocotb.top.pclk,2,unit="ns").start())
    bfm = apb4_slave_bfm()
    await bfm.reset()
    bfm.start_tasks()
    addr = 0x1004
    read_data = 0xFACD
    write = 0
    await bfm.send_read_command(addr,read_data,write)
    await compare_block(bfm.master_monitor_queue,bfm.backend_monitor_queue,write)   
    # await Timer(100,"ns")

