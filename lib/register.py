class Register():
    def __init__(self, address, name):
        self.address = address
        self.name = name
        self.size = 0
        self.bits = []
    
    def add_bit(self, bit):
        self.size += bit.size

        self.bits.append(bit)
        self.bits.sort(reverse=True)
    
    def only_write(self):
        for bit in self.bits:
            if 'R' in bit.access_type or 'WC' in bit.access_type or 'WS' in bit.access_type:
                return False
        
        return True

    def all_read(self):
        for bit in self.bits:
            if not 'R' in bit.access_type:
                return False

        return True
    
    def has_read(self):
        for bit in self.bits:
            if 'R' in bit.access_type:
                return True
        
        return False

    def only_read(self):
        for bit in self.bits:
            if 'W' in bit.access_type or 'WC' in bit.access_type or 'WS' in bit.access_type:
                return False
        
        return True

class Bit():
    def __init__(self, name, access_type, pos, from_cont, to_cont, reset_value, description = ''):
        self.name = name
        self.access_type = access_type
        self.pos = pos
        self.from_cont = from_cont
        self.to_cont = to_cont
        self.reset_value = reset_value
        self.description = description

        if len(pos) == 1:
            self.size = 1
        else:
            self.size = pos[0] - pos[1] + 1

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
    
    def __hash__(self):
        return hash(self.name)

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
        self.sv_code  = "  // " + self.name + "\n"
        self.sv_code += "  always_ff @(posedge HCLK, negedge HRESETn) begin\n"
        self.sv_code += "    if(!HRESETn) begin\n" 
        if self.reset[-1] == '\n':
            self.sv_code += self.reset[:-1]
        else:
            self.sv_code += self.reset
        self.sv_code += "    end\n    else begin\n"
        self.sv_code += self.body
        self.sv_code += "    end\n  end\n"

        return self.sv_code
    
    def __str__(self):
        return self.gen_sv_code()