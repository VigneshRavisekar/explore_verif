import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer
from slave_inf import *
import logging

log = logging.getLogger("cocotb")


def comparison_block(sent_data, received_cmd):
    """Compare the sent data with the received command"""
    assert str(sent_data[0]) == str(received_cmd[0]), f"Address mismatch: Sent {sent_data[0]}, Received {received_cmd[0]}"
    assert str(sent_data[1]) == str(received_cmd[1]), f"Data mismatch: Sent {sent_data[1]}, Received {received_cmd[1]}"
   

class apb_master_2_slave:

    def __init__(self, dut):

        self.dut = dut
        self.psel             =  getattr(self.dut, getattr(slave_inf, "%s_psel"%"s_apb"))
        self.pen              =  getattr(self.dut, getattr(slave_inf, "%s_pen"%"s_apb"))
        self.prdy             =  getattr(self.dut, getattr(slave_inf, "%s_prdy"%"s_apb"))
        self.paddr            =  getattr(self.dut, getattr(slave_inf, "%s_paddr"%"s_apb"))
        self.pwrite           =  getattr(self.dut, getattr(slave_inf, "%s_pwrite"%"s_apb"))
        self.pwdat            =  getattr(self.dut, getattr(slave_inf, "%s_pwdat"%"s_apb"))
        self.pstrb            =  getattr(self.dut, getattr(slave_inf, "%s_pstrb"%"s_apb"))
        self.pprot            =  getattr(self.dut, getattr(slave_inf, "%s_pprot"%"s_apb"))
        self.prdat            =  getattr(self.dut, getattr(slave_inf, "%s_prdat"%"s_apb"))
        self.pslverr          =  getattr(self.dut, getattr(slave_inf, "%s_pslverr"%"s_apb"))

class apb_slave_2_master:

    def __init__(self, dut):

        self.dut = dut
        self.prdy             =  getattr(self.dut, getattr(slave_inf, "%s_prdy"%"s_apb"))
        self.prdat            =  getattr(self.dut, getattr(slave_inf, "%s_prdat"%"s_apb"))
        self.pslverr          =  getattr(self.dut, getattr(slave_inf, "%s_pslverr"%"s_apb"))

class command_interface:

    def __init__(self, dut):

        self.dut = dut
        self.valid            =  getattr(self.dut, getattr(slave_inf, "%s_valid"%"command"))
        self.ready            =  getattr(self.dut, getattr(slave_inf, "%s_ready"%"command"))
        self.pwrite           =  getattr(self.dut, getattr(slave_inf, "%s_pwrite"%"command"))
        self.paddr            =  getattr(self.dut, getattr(slave_inf, "%s_paddr"%"command"))
        self.pwdata           =  getattr(self.dut, getattr(slave_inf, "%s_pwdata"%"command"))
        self.pstrb            =  getattr(self.dut, getattr(slave_inf, "%s_pstrb"%"command"))
        self.pprot            =  getattr(self.dut, getattr(slave_inf, "%s_pprot"%"command"))

    def receive_command(self):
        """Receive command from the DUT"""
        if self.valid.value == 1:
            self.ready.value = 1
            return [self.paddr,self.pwdata]
       
class response_interface:

    def __init__(self, dut):

        self.dut = dut
        self.valid            =  getattr(self.dut, getattr(slave_inf, "%s_valid"%"response"))
        self.ready            =  getattr(self.dut, getattr(slave_inf, "%s_ready"%"response"))
        self.prdata           =  getattr(self.dut, getattr(slave_inf, "%s_prdata"%"response"))
        self.pslverr          =  getattr(self.dut, getattr(slave_inf, "%s_pslverr"%"response"))

    async def send_response(self):
        """Send response to the DUT"""
        if self.ready.value == 1:
            self.valid.value = 1
            await RisingEdge(self.dut.pclk)
        self.valid.value = 0    

@cocotb.test()
async def apb4_basic_write(dut):
    """Test for basic write operation"""

    cocotb.start_soon(Clock(dut.pclk, 2, unit="ns").start())

    dut._log.info("Starting basic write test")

    # Reset the DUT
    dut.presetn.value = 0
    await Timer(2, unit="ns")
    dut.presetn.value = 1
    
    master = apb_master_2_slave(dut)
    slave = apb_slave_2_master(dut)
    cmd = command_interface(dut)
    rsp = response_interface(dut)

    await RisingEdge(dut.pclk)
    master.paddr.value = 0x00000004
    master.pstrb.value = 0xF
    master.pwrite.value = 1
    master.pwdat.value = 0xDEADBEEF
    master.psel.value = 1
    await RisingEdge(dut.pclk)
    master.pen.value = 1
    await RisingEdge(cmd.valid)
    sent_data = [master.paddr.value, master.pwdat.value]
    received_cmd = cmd.receive_command()
    await rsp.send_response()
    comparison_block(sent_data, received_cmd)
    await Timer(100, unit="ns")
