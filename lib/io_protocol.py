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
    def __init__(self, registers = None, addr_width = 12, data_width = 32, pready = False):
        self.addr_width = addr_width
        self.data_width = data_width
        self.pready = pready
        self.params_sv = ""

        super().__init__(registers)

    def gen_params(self):
        self.params_sv = "  APB_ADDR_WIDTH = " + str(self.addr_width) + ",\n"
        self.params_sv += "  APB_DATA_WIDTH = " + str(self.data_width)

        return self.params_sv

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

        if self.pready:
            self.IO += "  output logic [APB_DATA_WIDTH-1:0] o_PRDATA,\n"
            self.IO += "  output logic                      o_PREADY"
        else:
            self.IO += "  output logic [APB_DATA_WIDTH-1:0] o_PRDATA"

        return self.IO

    def gen_read_logic(self):
        self.read_logic = "  // Read logic\n  always_comb begin\n"
        self.read_logic += "    o_PRDATA = 'h0;\n\n"
        self.read_logic += "    case (i_PADDR)\n"

        for register in self.registers:
            if register.has_read():
                if register.all_read():
                    self.read_logic += "      `ADDRESS_" + register.name.upper() +":\n"
                    self.read_logic += "        o_PRDATA[" + str(register.size-1) + ":0] = r_" + register.name + ";\n"
                else:
                    self.read_logic += "      `ADDRESS_" + register.name.upper() +": begin\n"
                    for bit in register.bits:
                        if "R" in bit.access_type:
                            self.read_logic += "        o_PRDATA[" + bit.get_pos() + "] = r_" + register.name + "." + bit.name + ";\n"
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
            for bit in register.bits:
                if bit.reset_value[:2] == "0x":
                    self.write_logic.add_reset_SVline("      r_" + register.name + "." + bit.name + " <= 'h" + bit.reset_value[2:] + ";\n")
                else:
                    try:
                        self.write_logic.add_reset_SVline("      r_" + register.name + "." + bit.name + " <= 'd" + str(int(bit.reset_value)) + ";\n")
                    except:
                        self.write_logic.add_reset_SVline("      r_" + register.name + "." + bit.name + " <= " + bit.reset_value + ";\n")
            self.write_logic.add_reset_SVline("\n")

            # Bit write operation
            if register.all_write() and register.size == self.data_width:
                self.write_logic.add_back_body_SVline("          `ADDRESS_" + register.name.upper() +":")
                self.write_logic.add_back_body_SVline("\n            r_" + register.name + " <= i_PWDATA;\n")
            elif register.all_write():
                self.write_logic.add_back_body_SVline("          `ADDRESS_" + register.name.upper() +":")
                if register.size == 1:
                    self.write_logic.add_back_body_SVline("\n            r_" + register.name + " <= i_PWDATA[0];\n")
                else:
                    self.write_logic.add_back_body_SVline("\n            r_" + register.name + " <= i_PWDATA[" + str(register.size - 1) + ":0];\n")
            elif not register.only_read():
                self.write_logic.add_back_body_SVline("          `ADDRESS_" + register.name.upper() +":")
                self.write_logic.add_back_body_SVline(" begin\n")

                for bit in register.bits:
                    if 'WC' in bit.access_type:
                        if bit.size == 1:
                            self.write_logic.add_back_body_SVline("            r_" + register.name + "." + bit.name + " <= i_PWDATA[" + bit.get_pos() + "] ? 1'b0:r_" + register.name + "." + bit.name + ";\n")
                        else:
                            for i in range(bit.pos[1], bit.pos[0]+1):
                                bit_idx = str(i - bit.pos[1])
                                self.write_logic.add_back_body_SVline("            r_" + register.name + "." + bit.name + "[" + bit_idx + "]" + " <= i_PWDATA[" + str(i) + "] ? 1'b0:r_" + register.name + "." + bit.name + "[" + bit_idx + "]" + ";\n")
                    elif 'WS' in bit.access_type:
                        if bit.size == 1:
                            self.write_logic.add_back_body_SVline("            r_" + register.name + "." + bit.name + " <= i_PWDATA[" + bit.get_pos() + "] ? 1'b1:r_" + register.name + "." + bit.name + ";\n")
                        else:
                            for i in range(bit.pos[1], bit.pos[0]+1):
                                bit_idx = str(i - bit.pos[1])
                                self.write_logic.add_back_body_SVline("            r_" + register.name + "." + bit.name + "[" + bit_idx + "]" + " <= i_PWDATA[" + str(i) + "] ? 1'b1:r_" + register.name + "." + bit.name + "[" + bit_idx + "]" + ";\n")
                    elif 'W' in bit.access_type:
                        self.write_logic.add_back_body_SVline("            r_" + register.name + "." + bit.name + " <= i_PWDATA[" + bit.get_pos() + "];\n")

                self.write_logic.add_back_body_SVline("          end\n")

        self.write_logic.add_back_body_SVline("        endcase\n      end\n") 

        return self.write_logic

    def gen_assigns(self):
        if self.pready:
            self.assigns = "  // To APB\n  assign o_PREADY  = 1'b1;\n"
        else:
            self.assigns = ""

        return self.assigns