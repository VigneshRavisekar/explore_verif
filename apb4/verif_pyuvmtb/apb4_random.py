import vsc

@vsc.randobj
class APB4_Random_Write:

    def __init__(self):
        self.addr = vsc.rand_uint32_t()
        self.data = vsc.rand_uint32_t()
        self.strb = vsc.rand_bit_t(4)

    @vsc.constraint
    def addr_c(self):
        self.addr >= 0x1000
        self.addr <= 0x1FFF

@vsc.randobj
class APB4_Random_Read:

    def __init__(self):
        self.addr = vsc.rand_uint32_t()

    @vsc.constraint
    def addr_c(self):
        self.addr >=0x1000
        self.addr <=0x1FFF

@vsc.randobj
class Backend_Random_Read:

    def __init__(self):
        self.rsp_data  = vsc.rand_uint32_t()

