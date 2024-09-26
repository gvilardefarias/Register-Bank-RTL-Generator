from lib.input_parser import CSV_parser
from lib.io_protocol import APB_protocol

class RB_generator():
    def __init__(self, input_file_name, parser = None, io_protocol = None, registers = None, name = "register_bank"):
        self.name = name
        self.registers = registers

        if parser == None:
            self.parser = CSV_parser(input_file_name)
        else:
            parser.set_file_name(input_file_name)

            self.parser = parser
        
        if io_protocol == None:
            self.io_protocol = APB_protocol()
        else:
            self.io_protocol = io_protocol
    
    def parser_input(self):
        self.parser.open_input_file()

        self.registers = self.parser.create_registers()

        self.io_protocol.set_registers(self.registers)
    
    def gen_IO(self):
        self.IO  = ""
        for reg in self.registers:
            for bit in reg.bits:
                if bit.from_cont:
                    if len(bit.pos) == 1:
                        self.IO += "  input  logic " + 20*" " + "i_" + bit.name.lower() + ",\n" 
                    else:
                        strSize = "[" + str(bit.pos[0] - bit.pos[1]) + ":0]"
                        self.IO += "  input  logic " +(20-len(strSize))*" " + strSize + "i_" + bit.name.lower() + ",\n" 
        
        if self.IO != "":
            self.IO += "\n"

        for reg in self.registers:
            for bit in reg.bits:
                if bit.to_cont:
                    if len(bit.pos) == 1:
                        self.IO += "  output  logic " + 20*" " + "o_" + bit.name.lower() + ",\n" 
                    else:
                        strSize = "[" + str(bit.pos[0] - bit.pos[1]) + ":0]"
                        self.IO += "  output  logic " +(20-len(strSize))*" " + strSize + "o_" + bit.name.lower() + ",\n" 

        if self.IO != "":
            self.IO = "  // Controller IO\n" + self.IO[:-2]
        
        self.IO = self.io_protocol.gen_IO() + "\n\n" + self.IO
        
        return self.IO

    def gen_read_logic(self):
        self.read_logic = self.io_protocol.gen_read_logic()
        return self.read_logic

    def gen_write_logic(self, writeFf = None):
        if writeFf == None:
            self.writeFf = self.io_protocol.gen_write_logic()
        else:
            self.writeFf = writeFf
        wc_write = ""
        n_write = ""

        for reg in self.registers:
            for bit in reg.bits:
                if bit.from_cont:
                    if bit.access_type == "WC":
                        wc_write += "      if(i_" + bit.name.lower() + ")\n"
                        wc_write += "        r_" + reg.name + "." + bit.name + " <= i_" + bit.name.lower() + ";\n"
                    else:
                        n_write += "      r_" + reg.name + "." + bit.name + " <= i_" + bit.name.lower() + ";\n"

        if n_write != "":
            self.write_logic = n_write + "\n"
        if wc_write != "":
            self.write_logic += wc_write + "\n"
        
        self.writeFf.add_front_body_SVline(self.write_logic)

        return self.writeFf

    def gen_defines(self):
        self.defines = ""

        for reg in self.registers:
            self.defines += "`define ADDRESS_" + reg.name.upper() + "  " + str(self.io_protocol.addr_width) + "'d" + reg.address + "\n" 

        return self.defines

    def gen_params(self):
        self.params = self.io_protocol.gen_params()

        return self.params

    def gen_signals(self):
        self.signals = "  // Register definitions\n"

        for reg in self.registers:
            self.signals += "  struct packed {\n"
            for bit in reg.bits:
                if len(bit.pos) == 1:
                    self.signals += "    logic       " + bit.name + ";  //" + bit.description + "\n"
                else:
                    self.signals += "    logic [" + str(bit.pos[0]-bit.pos[1]) + ":0] " + bit.name + ";  //" + bit.description + "\n"
            self.signals += "  } r_" + reg.name + ";\n\n"
        
        return self.signals

    def gen_assigns(self):
        self.assigns = ""

        for reg in self.registers:
            for bit in reg.bits:
                if bit.to_cont:
                    self.assigns += "  assign o_" + bit.name.lower() + " = r_" + reg.name + "." + bit.name + ";\n"

        if self.assigns != "":
            self.assigns = "  // To controller\n" + self.assigns + "\n"
        
        self.assigns += self.io_protocol.gen_assigns()

        return self.assigns

    def gen_sv_code(self):
        self.sv_code  = "module " + self.name + " #(\n"
        self.sv_code += self.gen_params() + "\n)\n(\n"
        self.sv_code += self.gen_IO() + "\n);\n\n"
        self.sv_code += self.gen_signals() + "\n"
        self.sv_code += str(self.gen_write_logic()) + "\n"
        self.sv_code += self.gen_read_logic() + "\n"
        self.sv_code += self.gen_assigns() + "\n"
        self.sv_code += "endmodule"

        return self.sv_code
    
    def gen_define_file(self):
        define_f = open("output/" + self.name + ".svh", "w") 
        define_f.write(self.gen_defines())
        define_f.close()
    
    def gen_sv_file(self):
        sv_f = open("output/" + self.name + ".sv", "w") 
        sv_f.write(self.gen_sv_code())
        sv_f.close()

    def gen_rb(self):
        if self.registers == None:
            self.parser_input()

        self.gen_define_file()
        self.gen_sv_file()