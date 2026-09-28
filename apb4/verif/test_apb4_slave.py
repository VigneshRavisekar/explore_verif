import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer
from slave_inf import *

class apb_slave:

    def __init__(self, dut):
        self.dut = dut
        self.psel             =  getattr(self.dut, getattr(slave_inf, "%_psel"%"s_apb"))
        self.pen              =  getattr(self.dut, getattr(slave_inf, "%_pen"%"s_apb"))
        self.prdy             =  getattr(self.dut, getattr(slave_inf, "%_prdy"%"s_apb"))
        self.paddr            =  getattr(self.dut, getattr(slave_inf, "%_paddr"%"s_apb"))
        self.pwrite           =  getattr(self.dut, getattr(slave_inf, "%_pwrite"%"s_apb"))
        self.pwdat            =  getattr(self.dut, getattr(slave_inf, "%_pwdat"%"s_apb"))
        self.pstrb            =  getattr(self.dut, getattr(slave_inf, "%_pstrb"%"s_apb"))
        self.pprot            =  getattr(self.dut, getattr(slave_inf, "%_pprot"%"s_apb"))
        self.prdat            =  getattr(self.dut, getattr(slave_inf, "%_prdat"%"s_apb"))
        self.pslverr          =  getattr(self.dut, getattr(slave_inf, "%_pslverr"%"s_apb"))


@cocotb.test()
async def check(dut):

     cocotb.start_soon(Clock(dut.pclk, 10, unit="ns").start())
     dut.presetn.value = 0 
     await Timer(5,"ns")
     dut.presetn.value = 1
     await Timer(100, unit="ns")
        