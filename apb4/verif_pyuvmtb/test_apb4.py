import cocotb
import pyuvm 
from cocotb.triggers import Timer, RisingEdge, FallingEdge,ReadOnly
from cocotb.clock import Clock  
from pyuvm import *
from apb4_tb import *


@pyuvm.test()
class t_write_basic(uvm_test):

    def build_phase(self):

        ## Write_Packet
        self.addr      = 0x10
        self.data      = 0x20
        self.strb      = 0x3
        self.write     = 1
        write_packet = {"addr":self.addr,"data":self.data,"strb":self.strb,"write":self.write}
        self.env  = apb4_env("env",self)
        ConfigDB().set(self,"env.tester","WRITE_PACKET",write_packet)
