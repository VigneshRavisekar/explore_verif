SIM = verilator

TOPLEVEL_LANG = verilog

PWD := $(shell pwd)

TOPLEVEL = apb4_slave
COCOTB_TEST_MODULES = test_apb4_slave

VERILOG_SOURCES = \
    $(PWD)/rtl/apb4_slave.sv \
    $(PWD)/rtl/gaxi/gaxi_skid_buffer.sv

VERILOG_INCLUDE_DIRS = \
    $(PWD)/rtl_include

export PYTHONPATH := $(PWD)/verif
EXTRA_ARGS += --trace --trace-structs
EXTRA_ARGS += --no-timing

include $(shell cocotb-config --makefiles)/Makefile.sim