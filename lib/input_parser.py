from abc import ABC, abstractmethod
from register import Register, Bit
import csv

class Input_parser(ABC):
    def __init__(self, file_name):
        self.file_name = "input/"  + file_name
        self.registers = None

    def set_file_name(self, file_name):
        self.file_name = "input/"  + file_name

    @abstractmethod
    def open_input_file(self):
        pass

    @abstractmethod
    def create_registers(self):
        pass


class CSV_parser(Input_parser):
    def __init__(self, file_name):
        super().__init__(file_name)

    def open_input_file(self):
        input_file = open(self.file_name)
        self.csvDict = csv.DictReader(input_file)
        input_file.close()

    def create_registers(self):
        # Group registers by address
        addrMap     = {}
        
        for row in self.csvDict:
            try:
                addrMap[row['Register Address']].append(row)
            except:
                addrMap[row['Register Address']] = [row]

        for reg_addr in addrMap:
            reg_name = None

            for row in addrMap[reg_addr]:
                # Create Register if it doesnt exist
                if reg_name == None:
                    reg_name = row['Register Name']

                    register = Register(reg_addr, reg_name)

                pos = row['Position Bit'].split(":")
                pos = [int(pos[0]), int(pos[1])]

                access_type = row['Access'].split(' ')

                from_cont = int(row["From Controller"])
                to_cont = int(row["To Controller"])
          
                bit_name = row['Bit Name']
                bit_description = row['Functional Description']

                bit = Bit(bit_name, access_type, pos, from_cont, to_cont, bit_description)

                register.add_bit(bit)
            
            self.registers.append(register)
    
        return self.registers