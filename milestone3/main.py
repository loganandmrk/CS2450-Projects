import sys
from memory import Memory
#create base structure for the main class.
def main():
    #Read file from command line and parse the input data and run a function to manipulate it
    if len(sys.argv) != 2:
        print("File was not provided or too many arguments presented")
        sys.exit(1)
    
    filename = sys.argv[1]
    with open(filename, 'r') as file:
        lines = file.read().splitlines()
        memory = Memory()
        #Added Index for memory to be added in parsing
        index= 0

        for line in lines:
            sign = line[0] #sign of the instruction, either + or -
            instruction = line[1:3] #the 2 digit instruction of the program
            memory_loc = line[3:5] #the 2 digit memory location operations should be performed on
            value = line[1:5] #full integer

            #writes memory with index as key number, then stores parsed info into memory of key using a list.
            memory.write_inst(index, [sign, int(instruction), str(memory_loc), int(value), line])
            #print (memory.read(index))
            index += 1


    program_counter = 0
    run = True

    while run:
        #print(f"Current PC: {program_counter}, Read Result: {memory.read_inst(program_counter)} Accumulator: {memory.acumulator}")
        #print(memory.acumulator)
        opcode = int(memory.read_inst(program_counter)[1])
        if program_counter > 99:
            opcode=43
        match opcode:
            case 10:
                #READ
                memory.read(memory.read_inst(program_counter)[2])
            case 11:
                #WRITE
                memory.write(memory.read_inst(program_counter)[2])
            case 20:
                #LOAD
                memory.load(memory.read_inst(program_counter)[2])
            case 21:
                #STORE
                memory.store(memory.read_inst(program_counter)[2])
            case 30:
                #print(memory.read_inst(program_counter)[2])
                memory.add(memory.read_inst(program_counter)[2])
            case 31:
                memory.subtract(memory.read_inst(program_counter)[2])
            case 32:
                #DIVIDE
                memory.divide(memory.read_inst(program_counter)[2])
            case 33:
                #MULTIPLY
                memory.multiply(memory.read_inst(program_counter)[2])
            case 40:
                #BRANCH
                program_counter = int(memory.read_inst(program_counter)[2])
                continue
                
            case 41:
                #BRANCHNEG
                if memory.acumulator < 0:
                    program_counter = int(memory.read_inst(program_counter)[2])
                    continue 
                
            case 42:
                #BRANCHZERO
                if memory.acumulator == 0:
                    program_counter = int(memory.read_inst(program_counter)[2])
                    continue
                
            case 43:
                #HALT
                run = False
                break
                
            case _:
                print("Invalid instruction")
        program_counter += 1

if __name__ == "__main__":
    main()
