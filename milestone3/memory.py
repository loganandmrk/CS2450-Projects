#creates a dictionary with keys from 00 to 99 and sets values to None
#key values are currently strings and not ints since ints do not preserve leading zeros.
keys_tuple = tuple(f"{i:02d}" for i in range(100))
memory_dict = dict.fromkeys(keys_tuple, None)

#defines memory as a class with an init function that initializes the memory attribute to the memory_dict created above
class Memory:
    def __init__(self):
        self.memory = memory_dict
        self.acumulator = 0
        self.memory_size = 100
        self.word_min = -9999
        self.word_max = 9999

    def value_finder(self, address):
        if isinstance(self.memory[address], list):
            value = int(self.memory[address][4])
        else:
            value = self.memory[address]
        return value
    
    def truncation_acc(self):
        value = self.acumulator
        if value > self.word_max or value < self.word_min:
            if value < 0:
                value %= -10000
            if value > 0:
                value %= 10000

        self.acumulator = value
        return self.acumulator

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
        if int(address) < 0 or int(address) >= self.memory_size:
            raise ValueError("Address " + str(address) + " is not valid")
        user_input = input("Enter a word for memory location " + str(address) + ": ")

        try:
            value = int(user_input)
        except:
            raise ValueError(str(user_input) + " is not a valid number")
        
        if value < self.word_min or value > self.word_max:
            raise OverflowError(str(value) + " is out of range")
        
        self.memory[address] = value
    
    def write(self, address):
        if int(address) < 0 or int(address) >= self.memory_size:
            raise ValueError("Address " + str(address) + " is not valid")
        
        value = self.value_finder(address)
        
        if value < 0:
            print("-" + str(abs(value)).zfill(4))
        else:
            print(str(value).zfill(4))

    def load(self, address):
        if int(address) < 0 or int(address) >= self.memory_size:
            raise ValueError("Address " + str(address) + " is not valid")
        
        #added checker to make sure if the memory was already parsed that it gets the correct info loaded to accumulator.
        value = self.value_finder(address)
        self.acumulator = value
    
    def store(self, address):
        if int(address) < 0 or int(address) >= self.memory_size:
            raise ValueError("Address " + str(address) + " is not valid")
        
        if self.acumulator < self.word_min or self.acumulator > self.word_max:
            raise OverflowError("Accumulator value is out of range")
        
        self.memory[address] = self.acumulator
    
    def add(self, address):
        if int(address) < 0 or int(address) >= self.memory_size:
            raise ValueError("Address " + str(address) + " is not valid")
        value = self.value_finder(address)
        if value is None:
            raise ValueError("Memory location " + str(address) + " is empty")
        self.acumulator = self.acumulator + value
        self.truncation_acc()

    def subtract(self, address):
        if int(address) < 0 or int(address) >= self.memory_size:
            raise ValueError("Address " + str(address) + " is not valid")
        value = self.value_finder(address)
        if value is None:
            raise ValueError("Memory location " + str(address) + " is empty")
        self.acumulator = self.acumulator - value
        self.truncation_acc()

    def multiply(self, address):
        if int(address) < 0 or int(address) >= self.memory_size:
            raise ValueError("Address " + str(address) + " is not valid")
        value = self.value_finder(address)
        if value is None:
            raise ValueError("Memory location " + str(address) + " is empty")
        self.acumulator = self.acumulator * value
        self.truncation_acc()

    def divide(self, address):
        if int(address) < 0 or int(address) >= self.memory_size:
            raise ValueError("Address " + str(address) + " is not valid")
        value = self.value_finder(address)
        if value is None:
            raise ValueError("Memory location " + str(address) + " is empty")
        if value == 0:
            raise ValueError("Cannot divide by zero")
        self.acumulator = int(self.acumulator / value)
        self.truncation_acc()

