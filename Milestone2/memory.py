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

    def write(self, address, value):
        # Forces integer addresses into the "00" string format
        if isinstance(address, int):
            address = f"{address:02d}"
        self.memory[address] = value

    def read(self, address):
        if isinstance(address, int):
            address = f"{address:02d}"
        return self.memory[address]