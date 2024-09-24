from abc import ABC, abstractmethod

class IO_protocol(ABC):
    def __init__(self, registers):
        self.registers(registers)

    @abstractmethod
    def gen_io():
        pass

    @abstractmethod
    def gen_read_ff():
        pass

    @abstractmethod
    def gen_write_ff():
        pass

    @abstractmethod
    def gen_assigns():
        pass

    @abstractmethod
    def gen_signals():
        pass


class APB_protocol(IO_protocol):
    def __init__(self, registers, addr_width = 12, data_width = 32):
        self.addr_width = addr_width
        self.data_width = data_width

        super().__init__(registers)

    def gen_io():

    def gen_read_ff():

    def gen_write_ff():
        # Header
        self.writeFf  = "  always_ff @(posedge HCLK, negedge HRESETn) begin\n"
        self.writeFf += "    if(!HRESETn) begin\n" 

        writeOp = ''
        for register in registers:
            # Reset
            self.writeFf += "      r_" + register.name + " <= 'h0;\n"

            # Bit write operation
            if register.all_write():
                writeOp += "          `ADDRESS_" + register.name.upper() +":"
                writeOp += "\n            r_" + register.name + " <= i_PWDATA;\n"
            elif not register.all_read():
                writeOp += "          `ADDRESS_" + register.name.upper() +":"
                writeOp += " begin\n"
                for bit in registers.bits:
                    if 'WC' in access:
                        writeOp += "            r_" + register.name + "[" + bit.get_pos() + "] <= i_PWDATA[" + bit.get_pos() + "] ? 1'b0:r_" + register.name + "[" + bit.get_pos() + "];\n"
                    elif 'W' in access:
                        writeOp += "            r_" + register.name + "[" + bit.get_pos() + "] <= i_PWDATA[" + bit.get_pos() + "];\n"
                writeOp += "          end\n"
        
        self.writeFf += "    end\n    else begin\n"
        # Flipflop body
        self.writeFf += "      if (i_PSEL && i_PENABLE && i_PWRITE) begin\n        case (i_PADDR)\n"
        self.writeFf += writeOp
        self.writeFf += "        endcase\n      end\n    end\n  end\n"

        return writeFf

    def gen_assigns():

    def gen_signals():
