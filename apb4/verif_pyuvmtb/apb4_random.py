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


@vsc.randobj
class APB4_Random_Mix:

    def __init__(self):
        self.write = vsc.rand_bit_t(1)
        self.addr  = vsc.rand_uint32_t()
        self.data  = vsc.rand_uint32_t()
        self.strb  = vsc.rand_bit_t(4)

    @vsc.constraint
    def addr_c(self):
        vsc.dist(self.addr, [
            vsc.weight(vsc.rng(0x1001, 0x1FFE), 70),
            vsc.weight(0x1000, 5),
            vsc.weight(0x1FFF, 5),
            vsc.weight(vsc.rng(0x0000, 0x0FFF), 10),
            vsc.weight(vsc.rng(0x2000, 0x2FFF), 10),
        ])