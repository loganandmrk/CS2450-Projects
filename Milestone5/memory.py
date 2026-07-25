MEMORY_SIZE = 250
WORD_MIN = -999999
WORD_MAX = 999999
 
INSTRUCTION_MNEMONICS = {
    10: "READ",
    11: "WRITE",
    20: "LOAD",
    21: "STORE",
    30: "ADD",
    31: "SUBTRACT",
    32: "DIVIDE",
    33: "MULTIPLY",
    40: "BRANCH",
    41: "BRANCHNEG",
    42: "BRANCHZERO",
    43: "HALT",
}
 
 
def decode_instruction(value):
    magnitude = abs(int(value))
    if magnitude >= 100000:
        opcode = magnitude // 10000
        operand = magnitude % 10000
    elif magnitude >= 10000:
        opcode = magnitude // 1000
        operand = magnitude % 1000
    else:
        opcode = magnitude // 100
        operand = magnitude % 100
    return opcode, f"{operand:02d}"
 
 
def describe_word(value):
    if value is None:
        return "(empty)"
    opcode, operand = decode_instruction(value)
    if opcode == 43:
        return "HALT"
    if opcode in INSTRUCTION_MNEMONICS:
        return f"{INSTRUCTION_MNEMONICS[opcode]} {operand}"
    return "DATA"
 
 
def format_word(value):
    sign = "-" if value < 0 else "+"
    return f"{sign}{abs(value):06d}"
 
 
def parse_word(text):
    text = text.strip()
    try:
        value = int(text)
    except ValueError:
        raise ValueError(f"'{text}' is not a valid whole number")
    if value < WORD_MIN or value > WORD_MAX:
        raise OverflowError(f"{value} is outside the allowed range ({WORD_MIN} to {WORD_MAX})")
    return value


def convert_4_digit_to_6_digit(text):
    text = text.strip()
    sign = ""
    if text.startswith("+"):
        text = text[1:]
    elif text.startswith("-"):
        sign = "-"
        text = text[1:]

    if len(text) != 4 or not text.isdigit():
        return f"{sign}{text}"

    opcode = int(text[:2])
    operand = int(text[2:])

    if opcode not in INSTRUCTION_MNEMONICS:
        return f"{sign}{text}"

    if operand < 0 or operand > 99:
        return f"{sign}{text}"

    if text[:2] == text[2:]:
        return f"{sign}{text}"

    return f"{sign}0{text[:2]}0{text[2:]}"
 
 
class Memory:
    def __init__(self):
        self.memory = {f"{i:02d}": None for i in range(MEMORY_SIZE)}
        self.acumulator = 0
        self.memory_size = MEMORY_SIZE
        self.word_min = WORD_MIN
        self.word_max = WORD_MAX
 
    def _validate_address(self, address):
        if int(address) < 0 or int(address) >= self.memory_size:
            raise ValueError("Address " + str(address) + " is not valid")
 
    @staticmethod
    def _address_key(address):
        if isinstance(address, int):
            return f"{address:02d}"
        return address
 
    def value_finder(self, address):
        return self.memory[address]
 
    def truncation_acc(self):
        value = self.acumulator
        if value > self.word_max or value < self.word_min:
            if value < 0:
                value %= -1000000
            if value > 0:
                value %= 1000000
        self.acumulator = value
        return self.acumulator
 
    def write_inst(self, address, value):
        self.memory[self._address_key(address)] = value
 
    def read_inst(self, address):
        return self.memory[self._address_key(address)]
 
    def read(self, address, user_input):
        self._validate_address(address)
        try:
            value = int(user_input)
        except (ValueError, TypeError):
            raise ValueError(str(user_input) + " is not a valid number")
        if value < self.word_min or value > self.word_max:
            raise OverflowError
        self.memory[address] = value
 
    def write(self, address):
        self._validate_address(address)
        value = self.value_finder(address)
        if value is None:
            raise ValueError("Memory location " + str(address) + " is empty")
        if value < 0:
            return "-" + str(abs(value)).zfill(6)
        else:
            return str(value).zfill(6)
 
    def load(self, address):
        self._validate_address(address)
        value = self.value_finder(address)
        if value is None:
            raise ValueError("Memory location " + str(address) + " is empty")
        self.acumulator = value
 
    def store(self, address):
        self._validate_address(address)
        if self.acumulator < self.word_min or self.acumulator > self.word_max:
            raise OverflowError("Accumulator value is out of range")
        self.memory[address] = self.acumulator
 
    def add(self, address):
        self._validate_address(address)
        value = self.value_finder(address)
        if value is None:
            raise ValueError("Memory location " + str(address) + " is empty")
        self.acumulator = self.acumulator + value
        self.truncation_acc()
 
    def subtract(self, address):
        self._validate_address(address)
        value = self.value_finder(address)
        if value is None:
            raise ValueError("Memory location " + str(address) + " is empty")
        self.acumulator = self.acumulator - value
        self.truncation_acc()
 
    def multiply(self, address):
        self._validate_address(address)
        value = self.value_finder(address)
        if value is None:
            raise ValueError("Memory location " + str(address) + " is empty")
        self.acumulator = self.acumulator * value
        self.truncation_acc()
 
    def divide(self, address):
        self._validate_address(address)
        value = self.value_finder(address)
        if value is None:
            raise ValueError("Memory location " + str(address) + " is empty")
        if value == 0:
            raise ValueError("Cannot divide by zero")
        self.acumulator = int(self.acumulator / value)
        self.truncation_acc()

