class Register():
    def __init__(self, address, name):
        self.address = address
        self.name = name
        self.bits = set() 
    
    def add_bit(bit):
        self.bits.add(bit)
    
    def all_write():
        for bit in bits:
            if 'R' in bit.access_type or 'WC' in bit.access_type:
                return False
        
        return True

    def all_read():
        for bit in bits:
            if 'W' in bit.access_type or 'WC' in bit.access_type:
                return False
        
        return True

class Bit():
    def __init__(self, name, access_type, pos, from_cont, to_cont, description = ''):
        self.name = name
        self.access_type = access_type
        self.pos = pos
        self.from_cont = from_cont
        self.to_cont = to_cont
        self.description = description

    def get_pos(self):
        return ':'.join(str(i) for i in self.pos)

    def __lt__(self, obj):
        return ((self.pos[-1]) < (obj.pos[-1]))

    def __gt__(self, obj):
        return ((self.pos[-1]) > (obj.pos[-1]))

    def __le__(self, obj):
        return ((self.pos[-1]) <= (obj.pos[-1]))

    def __ge__(self, obj):
        return ((self.pos[-1]) >= (obj.pos[-1]))

    def __eq__(self, obj):
        return (self.pos[-1] == obj.pos[-1])

class FlipFlop():
    def __init__(self, name = "", reset = "", body = ""):
        self.name = name
        self.reset = reset
        self.body = body
    
    def add_reset_SVline(self, reset_line):
        self.reset += reset_line
    
    def add_front_body_SVline(self, body_line):
        self.body = body_line + self.body

    def add_back_body_SVline(self, body_line):
        self.body += body_line

    def gen_sv_code(self):
        self.sv_code  = "  always_ff @(posedge HCLK, negedge HRESETn) begin\n"
        self.sv_code += "    if(!HRESETn) begin\n" 
        self.sv_code += self.reset
        self.sv_code += "    end\n    else begin\n"
        self.sv_code += "      if (i_PSEL && i_PENABLE && i_PWRITE) begin\n        case (i_PADDR)\n"
        self.sv_code += self.body
        self.sv_code += "        endcase\n      end\n    end\n  end\n"