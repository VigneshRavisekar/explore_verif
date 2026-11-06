import cocotb
import pyuvm
from pyuvm import *


class APB4_Sequence_Item(uvm_sequence_item):

    def __init__(self, name, addr=0, data=0, strb=0, write=0):
        super().__init__(name)
        self.apb4_addr = addr
        self.apb4_data = data
        self.apb4_strb = strb
        self.apb4_write = write

    def __str__(self):
        return (
            f"{self.get_name()}: "
            f"addr:{self.apb4_addr} "
            f"data:{self.apb4_data} "
            f"strb:{self.apb4_strb} "
            f"write:{self.apb4_write}"
        )


class APB4_Sequence(uvm_sequence):

    async def body(self):

        
        packet = APB4_Sequence_Item("packet")
        await self.start_item(packet)
        self.supply_packet(packet)
        await self.finish_item(packet)

    def supply_packet(self, packet):
        pass


class APB4_Write_Seq(APB4_Sequence):

    def supply_packet(self, packet):
        packet.apb4_addr = 0x10
        packet.apb4_data = 0x20
        packet.apb4_strb = 0x1
        packet.apb4_write = 1

        


