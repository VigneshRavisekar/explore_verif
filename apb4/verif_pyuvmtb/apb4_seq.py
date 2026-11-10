import cocotb
import pyuvm
from pyuvm import *
from apb4_random import *


class APB4_Sequence_Item(uvm_sequence_item):

    def __init__(self, name, addr=0, data=0, strb=0, write=0,count=1):
        super().__init__(name)
        self.apb4_addr  = addr
        self.apb4_data  = data
        self.apb4_strb  = strb
        self.apb4_write = write
        self.count      = count
       


    def __str__(self):
        return (
            f"{self.get_name()}: "
            f"addr:{self.apb4_addr} "
            f"data:{self.apb4_data} "
            f"strb:{self.apb4_strb} "
            f"write:{self.apb4_write}"
        )

    
class Backend_Sequence_Item(uvm_sequence_item):

    def __init__(self,name,count=1):
        super().__init__(name)
        self.rsp_data  = 0
        self.count     = count


    def __str__(self):
        return (
            f"{self.get_name()}: "
            f"data:{self.rsp_data} "
)


class APB4_Sequence(uvm_sequence):

    async def body(self):

        for transaction_index in range(self.count):
            packet = APB4_Sequence_Item(f"packet_{transaction_index}")
            await self.start_item(packet)
            self.supply_packet(packet,transaction_index)
            await self.finish_item(packet)

    def supply_packet(self,packet,transaction_index):
        pass

class Backend_Sequence(uvm_sequence):

    async def body(self):

        for transaction_index in range(self.count):
            b_packet = Backend_Sequence_Item(f"b_packet{transaction_index}")
            await self.start_item(b_packet)
            self.backend_packet(b_packet,transaction_index)
            await self.finish_item(b_packet)

    def backend_packet(self,packet,transaction_index):
        pass

class APB4_Write_Seq(APB4_Sequence):

    
    def __init__(self, name="APB4_Write_Seq"):

      
        super().__init__(name)
        self.apb4_addr_list = [0x1000,0x1400,0x1250]
        self.apb4_data_list = [0x20,0x30,0x40]
        self.randomizer = APB4_Random_Write()
        self.random_mode = False



    def supply_packet(self, packet,transaction_index):

        if self.random_mode == False:
            
            packet.apb4_addr = self.apb4_addr_list[transaction_index]
            packet.apb4_data = self.apb4_data_list[transaction_index]
            packet.apb4_strb = 0xF
        else:
             self.randomizer.randomize()
             packet.apb4_addr = int(self.randomizer.addr)
             packet.apb4_data = int(self.randomizer.data)
             packet.apb4_strb = int(self.randomizer.strb)

        packet.apb4_write = 1

class Backend_Seq(Backend_Sequence):

        def __init__(self, name="Backend_Seq"):

            super().__init__(name)
            self.rsp_data_list = [0x20,0x30,0x40]
            self.randomizer    = Backend_Random_Read()
            self.random_mode   = False 
            

        def backend_packet(self,b_packet,transaction_index):

            if self.random_mode == False:

                b_packet.rsp_data = self.rsp_data_list[transaction_index]

            else:

                b_packet.rsp_data = int(self.randomizer.rsp_data)

class APB4_Read_Seq(APB4_Sequence):

        
    def __init__(self, name="APB4_Write_Seq"):

        ## you could modify here for changing address, data, strb
        super().__init__(name)
        self.apb4_addr_list = [0x1000,0x1400,0x1250]
        self.randomizer     = APB4_Random_Read()
        self.random_mode    = False

    def supply_packet(self, packet,transaction_index):

        if self.random_mode == False:
            packet.apb4_addr = self.apb4_addr_list[transaction_index]
        else:
            self.randomizer.randomize()
            packet.apb4_addr = int(self.randomizer.addr)
        


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


            
      


