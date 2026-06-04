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
        index= 00
        for line in lines:
            sign = line[0] #sign of the instruction, either + or -
            instruction = line[1:3] #the 2 digit instruction of the program
            memory_loc = line[3:5] #the 2 digit memory location operations should be performed on

            #writes memory with index as key number, then stores parsed info into memory of key using a list.
            memory.write(index, [sign, instruction, memory_loc, line])
            #prints memory at index
            print (memory.read(index))
            index += 1

        
    
    
        #Use Memory().memory to access the dictionary.
        #print(Memory().memory)
    program_counter = 00
    run = True
    opcode = memory.read(program_counter)[1]
    while run:
        if program_counter > 99:
            opcode=43
        match opcode:
            case 10:
                #READ
                pass
            case 11:
                #WRITE
                pass
            case 20:
                #LOAD
                pass
            case 21:
                #STORE
                pass
            case 30:
                #ADD
                pass
            case 31:
                #SUBTRACT
                pass
            case 32:
                #DIVIDE
                pass
            case 33:
                #MULTIPLY
                pass
            case 40:
                program_counter = memory.read(program_counter)[2] 
                continue
                #BRANCH
            case 41:
                if memory.acumulator < 0:
                    program_counter = memory.read(program_counter)[2]
                continue 
                #BRANCHNEG
            case 42:
                if memory.acumulator == 0:
                    program_counter = memory.read(program_counter)[2]
                continue
                #BRANCHZERO
            case 43:
                run = False
                continue
                #HALT
            case _:
                print("Invalid instruction")
        program_counter += 1

if __name__ == "__main__":
    main()