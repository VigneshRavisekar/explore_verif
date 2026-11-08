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

    
class Backend_Sequence_Item(uvm_sequence_item):

    def __init__(self,name):
        super().__init__(name)
        self.rsp_data  = 0
        
    def __str__(self):
        return (
            f"{self.get_name()}: "
            f"data:{self.rsp_data} "
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
        packet.apb4_addr = 0x1000
        packet.apb4_data = 0x20
        packet.apb4_strb = 0x1
        packet.apb4_write = 1

class APB4_Error_Write_Seq(APB4_Sequence):

    def supply_packet(self, packet):
        packet.apb4_addr = 0x2000
        packet.apb4_data = 0x20
        packet.apb4_strb = 0x1
        packet.apb4_write = 1

class APB4_Read_Seq(APB4_Sequence):

    def supply_packet(self, packet):
        packet.apb4_addr = 0x1000
        packet.apb4_write = 0

class APB4_Error_Read_Seq(APB4_Sequence):

    def supply_packet(self, packet):
        packet.apb4_addr = 0x2000
        packet.apb4_write = 0

class Backend_Seq(uvm_sequence):

    async def body(self):

        b_packet = Backend_Sequence_Item("b_packet")
        await self.start_item(b_packet)
        b_packet.rsp_data = 0x20
        await self.finish_item(b_packet)


class APB4_Pattern_WALK_ONE_ZERO(APB4_Sequence):
    """32 writes: address walks 1; write data walks 0."""

    async def body(self):
        for bit_index in range(32):
            packet = APB4_Sequence_Item(f"walk_pattern_{bit_index}")

            # Walking-1 address: 0x00000001 through 0x80000000.
            packet.apb4_addr = 1 << bit_index

            # Walking-0 data, explicitly limited to 32 bits.
            packet.apb4_data = (~(1 << bit_index)) & 0xFFFFFFFF

            packet.apb4_strb = 0x1
            packet.apb4_write = 1

            await self.start_item(packet)
            await self.finish_item(packet)

class Backend_Pattern_Seq(Backend_Seq):
    """Supply one backend sequence item for each of the 32 write commands.

    The current backend_driver requests an item for every command, including
    writes. rsp_data is not used by that driver for a write command, but the
    item is still required to complete its sequencer handshake.
    """

    async def body(self):
        for transaction_index in range(32):
            b_packet = Backend_Sequence_Item(
                f"backend_pattern_{transaction_index}"
            )
            b_packet.rsp_data = 0
            await self.start_item(b_packet)
            await self.finish_item(b_packet)

            

        


