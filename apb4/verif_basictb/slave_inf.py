from pathlib import Path

# APB4 interface signal-name mapping used by the basic Cocotb testbench.
# Preserved from the original verif directory.
class slave_inf:
    s_apb_psel = "s_apb_PSEL"
    s_apb_pen = "s_apb_PENABLE"
    s_apb_prdy = "s_apb_PREADY"
    s_apb_paddr = "s_apb_PADDR"
    s_apb_pwrite = "s_apb_PWRITE"
    s_apb_pwdat = "s_apb_PWDATA"
    s_apb_pstrb = "s_apb_PSTRB"
    s_apb_pprot = "s_apb_PPROT"
    s_apb_prdat = "s_apb_PRDATA"
    s_apb_pslverr = "s_apb_PSLVERR"
    command_valid = "cmd_valid"
    command_ready = "cmd_ready"
    command_pwrite = "cmd_pwrite"
    command_paddr = "cmd_paddr"
    command_pwdata = "cmd_pwdata"
    command_pstrb = "cmd_pstrb"
    command_pprot = "cmd_pprot"
    response_valid = "rsp_valid"
    response_ready = "rsp_ready"
    response_prdata = "rsp_prdata"
    response_pslverr = "rsp_pslverr"
