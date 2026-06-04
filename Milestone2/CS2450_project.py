MEMORY_SIZE = 100
WORD_MIN = -9999
WORD_MAX = 9999


def read(state, address):
    if address < 0 or address >= MEMORY_SIZE:
        raise ValueError("Address " + str(address) + " is not valid")
    
    user_input = input("Enter a word for memory location " + str(address) + ": ")
    
    try:
        value = int(user_input)
    except:
        raise ValueError(str(user_input) + " is not a valid number")
    
    if value < WORD_MIN or value > WORD_MAX:
        raise OverflowError(str(value) + " is out of range")
    
    state["memory"][address] = value


def write(state, address):
    if address < 0 or address >= MEMORY_SIZE:
        raise ValueError("Address " + str(address) + " is not valid")
    
    value = state["memory"][address]
    
    if value < 0:
        print("-" + str(abs(value)).zfill(4))
    else:
        print("+" + str(value).zfill(4))


def load(state, address):
    if address < 0 or address >= MEMORY_SIZE:
        raise ValueError("Address " + str(address) + " is not valid")
    
    state["accumulator"] = state["memory"][address]


def store(state, address):
    if address < 0 or address >= MEMORY_SIZE:
        raise ValueError("Address " + str(address) + " is not valid")
    
    if state["accumulator"] < WORD_MIN or state["accumulator"] > WORD_MAX:
        raise OverflowError("Accumulator value is out of range")
    
    state["memory"][address] = state["accumulator"]
