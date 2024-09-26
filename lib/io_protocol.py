from abc import ABC, abstractmethod
from register import FlipFlop

class IO_protocol(ABC):
    def __init__(self, registers = None):
        self.registers = registers

    def set_registers(self, registers):
        self.registers = registers

    @abstractmethod
    def gen_IO(self):
        pass

    @abstractmethod
    def gen_params(self):
        pass

    @abstractmethod
    def gen_read_logic(self):
        pass

    @abstractmethod
    def gen_write_logic(self):
        pass

    @abstractmethod
    def gen_assigns(self):
        pass


class APB_protocol(IO_protocol):
    def __init__(self, registers = None, addr_width = 12, data_width = 32):
        self.addr_width = addr_width
        self.data_width = data_width

        super().__init__(registers)

    def gen_params(self):
        self.defines += "  APB_ADDR_WIDTH = " + str(self.addr_width) + ",\n"
        self.defines += "  APB_DATA_WIDTH = " + str(self.data_width)

        return self.defines

    def gen_IO(self):
        self.IO  = "   // APB IO\n"
        self.IO += "   input  logic                      HCLK,\n"
        self.IO += "   input  logic                      HRESETn,\n"
        self.IO += "   input  logic [APB_ADDR_WIDTH-1:0] i_PADDR,\n"
        self.IO += "   input  logic [APB_DATA_WIDTH-1:0] i_PWDATA,\n"
        self.IO += "   input  logic                      i_PWRITE,\n"
        self.IO += "   input  logic                      i_PSEL,\n"
        self.IO += "   input  logic                      i_PENABLE,\n"
        self.IO += "   \n"
        self.IO += "   output logic [APB_DATA_WIDTH-1:0] o_PRDATA,\n"
        self.IO += "   output logic                      o_PREADY,\n"
        self.IO += "   output logic                      o_PSLVERR"

        return self.IO

    def gen_read_logic(self, readFf = None):
        self.read_logic += "  always_comb begin\n    case (s_apb_addr)\n"

        for register in self.registers:
            self.read_logic += "      `ADDRESS_" + register.name.upper() +":\n"
            self.read_logic += "        o_PRDATA = r_" + register.name + ";\n"

        self.read_logic += "      default:\n        o_PRDATA = 'h0;\n"
        self.read_logic += "    endcase\n  end\n"

        return self.read_logic

    def gen_write_logic(self, write_logic = None):
        if write_logic != None:
            self.write_logic  = FlipFlop("Write FlipFlop")

        for register in self.registers:
            # Reset
            self.write_logic.add_reset_SVline("      r_" + register.name + " <= 'h0;\n")

            # Bit write operation
            if register.all_write():
                self.write_logic.add_back_body_SVline("          `ADDRESS_" + register.name.upper() +":")
                self.write_logic.add_back_body_SVline("\n            r_" + register.name + " <= i_PWDATA;\n")
            elif not register.all_read():
                self.write_logic.add_back_body_SVline("          `ADDRESS_" + register.name.upper() +":")
                self.write_logic.add_back_body_SVline(" begin\n")
                for bit in register.bits:
                    if 'WC' in bit.access:
                        self.write_logic.add_back_body_SVline("            r_" + register.name + "[" + bit.get_pos() + "] <= i_PWDATA[" + bit.get_pos() + "] ? 1'b0:r_" + register.name + "[" + bit.get_pos() + "];\n")
                    elif 'W' in bit.access:
                        self.write_logic.add_back_body_SVline("            r_" + register.name + "[" + bit.get_pos() + "] <= i_PWDATA[" + bit.get_pos() + "];\n")
                self.write_logic.add_back_body_SVline("          end\n")
        
        return self.write_logic

    def gen_assigns(self):
        self.assigns = "  assign PREADY  = 1'b1;\n  assign PSLVERR = 1'b0;\n\n"

        return self.assigns