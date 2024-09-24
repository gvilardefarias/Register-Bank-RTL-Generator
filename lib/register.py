class Register():
    def __init__(self, address, name):
        self.address = address
        self.name = name
        self.bits = set() 
    
    def add_bit(bit):
        self.bits.add(bit)

class Bit():
    def __init__(self, name, access_type, pos, description = ''):
        self.name = name
        self.access_type = access_type
        self.pos = pos
        self.description = description

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