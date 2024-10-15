from abc import ABC, abstractmethod
import csv
from lib.register import Register, Bit

class Input_parser(ABC):
    def __init__(self, file_name):
        self.file_name = "input/"  + file_name + ".csv"
        self.registers = []

    def set_file_name(self, file_name):
        self.file_name = "input/"  + file_name + ".csv"

    @abstractmethod
    def open_input_file(self):
        pass

    @abstractmethod
    def create_registers(self):
        pass

class CSV_parser(Input_parser):
    def __init__(self, file_name, delimiter = ","):
        super().__init__(file_name)

        self.delimiter = delimiter

    def open_input_file(self):
        input_file = open(self.file_name)
        self.csvDict = csv.DictReader(input_file, delimiter = self.delimiter)

    def create_registers(self):
        # Group registers by address
        addrMap     = {}
        
        p_row = None  # Previous line
        for row in self.csvDict:
            if p_row != None:
                if row['Addr'] == '':
                    row['Addr'] = p_row['Addr']
                    row['Reg Name'] = p_row['Reg Name']
                if row['Position'] == '':
                    continue
            try:
                addrMap[row['Addr']].append(row)
            except:
                addrMap[row['Addr']] = [row]
            
            p_row = row

        for reg_addr in addrMap:
            reg_name = None

            p_row = None  # Previous line
            for row in addrMap[reg_addr]:
                # Create Register if it doesnt exist
                if reg_name == None:
                    reg_name = row['Reg Name']

                    if reg_addr[:2] == "0x":
                        reg_addr = reg_addr[2:]

                    register = Register(reg_addr, reg_name)

                pos = row['Position'].strip("[]").split(":")
                if len(pos) == 1:
                    pos = [int(pos[0])]
                else:
                    pos = [int(pos[0]), int(pos[1])]

                access_type = row['Field access'].split(' ')

                to_cont = 0
                from_cont = 0
                if 'External access' in row:
                    external_access_type = row['External access'].split(' ')
                    if 'R' in external_access_type:
                        to_cont = 1
                    if 'W' in external_access_type:
                        from_cont = 1
          
                bit_name = row['Fields']
                bit_description = row['Field Description']
                bit_description = bit_description.replace("\n"," ")

                if 'Reset value' in row:
                    reset_value = row['Reset value']
                else:
                    reset_value = "0x0";

                bit = Bit(bit_name, access_type, pos, from_cont, to_cont, reset_value, bit_description)

                register.add_bit(bit)
            
            self.registers.append(register)
    
        return self.registers