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
            vsc.weight(vsc.rng(0x1001, 0x1FFE), 40),
            vsc.weight(0x1000, 5),
            vsc.weight(0x1FFF, 5),
            vsc.weight(vsc.rng(0x0000, 0x0FFF), 30),
            vsc.weight(vsc.rng(0x2000, 0x2FFF), 20),
        ])

    def mode_c(self):

        vsc.dist(self.write,[vsc.weight(0,50),vsc.weight(1,50)])


@vsc.covergroup
class CG1(object):

    def __init__(self):
        self.with_sample(write = vsc.bit_t(1), err   = vsc.bit_t(1))

        self.mode_operation = vsc.coverpoint(self.write,bins={"wr":vsc.bin(1),"rd":vsc.bin(0)})
        self.error          = vsc.coverpoint(self.err,bins={"err":vsc.bin(1),"no_err":vsc.bin(0)})
        self.err_op_cross   = vsc.cross([self.mode_operation,self.error])