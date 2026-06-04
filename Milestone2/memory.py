from Milestone2.CS2450_project import WORD_MAX, WORD_MIN
import functions

#creates a dictionary with keys from 00 to 99 and sets values to None
#key values are currently strings and not ints since ints do not preserve leading zeros.
keys_tuple = tuple(f"{i:02d}" for i in range(100))
memory_dict = dict.fromkeys(keys_tuple, None)

#defines memory as a class with an init function that initializes the memory attribute to the memory_dict created above
class Memory:
    def __init__(self):
        self.memory = memory_dict
        self.acumulator = 0
        self.MEMORY_SIZE = 100
        self.WORD_MIN = -9999
        self.WORD_MAX = 9999

    def write_inst(self, address, value):
        # Forces integer addresses into the "00" string format
        if isinstance(address, int):
            address = f"{address:02d}"
        self.memory[address] = value

    def read_inst(self, address):
        if isinstance(address, int):
            address = f"{address:02d}"
        return self.memory[address]
    
    def read(self, address):
        if address < 0 or address >= self.MEMORY_SIZE:
            raise ValueError("Address " + str(address) + " is not valid")

        user_input = input("Enter a word for memory location " + str(address) + ": ")
        
        try:
            value = int(user_input)
        except:
            raise ValueError(str(user_input) + " is not a valid number")
        
        if value < self.WORD_MIN or value > self.WORD_MAX:
            raise OverflowError(str(value) + " is out of range")
        
        self.memory[address] = value