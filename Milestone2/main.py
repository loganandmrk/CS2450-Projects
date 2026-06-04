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
        for line in lines:
            sign = line[0] #sign of the instruction, either + or -
            instruction = line[1:3] #the 2 digit instruction of the program
            memory_loc = line[3:5] #the 2 digit memory location operations should be performed on

            #initialize memory values based on input file.
            memory.memory[memory_loc] = sign + instruction
            #case tree for instructions should go here
            match memory.memory[memory_loc][1:3]:
                case "10":
                    #READ
                    pass
                case "11":
                    #WRITE
                    pass
                case "20":
                    #LOAD
                    pass
                case "21":
                    #STORE
                    pass
                case "30":
                    #ADD
                    pass
                case "31":
                    #SUBTRACT
                    pass
                case "32":
                    #DIVIDE
                    pass
                case "33":
                    #MULTIPLY
                    pass
                case "40":
                    #BRANCH
                    pass
                case "41":
                    #use memory.memory[memory_loc][0] to access the sign
                    #BRANCHNEG
                    pass
                case "42":
                    #BRANCHZERO
                    pass
                case "43":
                    #HALT
                    pass
                case _:
                    print("Invalid instruction")

if __name__ == "__main__":
    main()