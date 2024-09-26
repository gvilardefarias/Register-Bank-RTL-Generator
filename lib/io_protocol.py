from abc import ABC, abstractmethod
from lib.register import FlipFlop

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
        self.params = "  APB_ADDR_WIDTH = " + str(self.addr_width) + ",\n"
        self.params += "  APB_DATA_WIDTH = " + str(self.data_width)

        return self.params

    def gen_IO(self):
        self.IO  = "  // APB IO\n"
        self.IO += "  input  logic                      HCLK,\n"
        self.IO += "  input  logic                      HRESETn,\n"
        self.IO += "  input  logic [APB_ADDR_WIDTH-1:0] i_PADDR,\n"
        self.IO += "  input  logic [APB_DATA_WIDTH-1:0] i_PWDATA,\n"
        self.IO += "  input  logic                      i_PWRITE,\n"
        self.IO += "  input  logic                      i_PSEL,\n"
        self.IO += "  input  logic                      i_PENABLE,\n"
        self.IO += "   \n"
        self.IO += "  output logic [APB_DATA_WIDTH-1:0] o_PRDATA,\n"
        self.IO += "  output logic                      o_PREADY,\n"
        self.IO += "  output logic                      o_PSLVERR"

        return self.IO

    def gen_read_logic(self):
        self.read_logic = "  // Read logic\n  always_comb begin\n    case (s_apb_addr)\n"

        for register in self.registers:
            if not register.only_write():
                if register.all_read():
                    self.read_logic += "      `ADDRESS_" + register.name.upper() +":\n"
                    self.read_logic += "        o_PRDATA = r_" + register.name + ";\n"
                else:
                    self.read_logic += "      `ADDRESS_" + register.name.upper() +": begin\n"
                    self.read_logic += "        o_PRDATA = 'h0;\n"
                    for bit in register.bits:
                        if "R" in bit.access_type:
                            self.read_logic += "        o_PRDATA[" + bit.get_pos() + "]" + " = r_" + register.name + "." + bit.name + ";\n"
                    self.read_logic += "      end\n"



        self.read_logic += "      default:\n        o_PRDATA = 'h0;\n"
        self.read_logic += "    endcase\n  end\n"

        return self.read_logic

    def gen_write_logic(self, write_logic = None):
        if write_logic == None:
            write_logic  = FlipFlop("Write FlipFlop")
        self.write_logic = write_logic

        self.write_logic.add_back_body_SVline("      if (i_PSEL && i_PENABLE && i_PWRITE) begin\n        case (i_PADDR)\n")
        for register in self.registers:
            # Reset
            self.write_logic.add_reset_SVline("      r_" + register.name + " <= 'h0;\n")

            # Bit write operation
            if register.only_write():
                self.write_logic.add_back_body_SVline("          `ADDRESS_" + register.name.upper() +":")
                self.write_logic.add_back_body_SVline("\n            r_" + register.name + " <= i_PWDATA;\n")
            elif not register.only_read():
                self.write_logic.add_back_body_SVline("          `ADDRESS_" + register.name.upper() +":")
                self.write_logic.add_back_body_SVline(" begin\n")
                for bit in register.bits:
                    if 'WC' in bit.access_type:
                        self.write_logic.add_back_body_SVline("            r_" + register.name + "." + bit.name + " <= i_PWDATA[" + bit.get_pos() + "] ? 1'b0:r_" + register.name + "." + bit.name + ";\n")
                    elif 'W' in bit.access_type:
                        self.write_logic.add_back_body_SVline("            r_" + register.name + "." + bit.name + " <= i_PWDATA[" + bit.get_pos() + "];\n")
                self.write_logic.add_back_body_SVline("          end\n")
        
        return self.write_logic

    def gen_assigns(self):
        self.assigns = "  // To APB\n  assign PREADY  = 1'b1;\n  assign PSLVERR = 1'b0;\n"

        return self.assigns