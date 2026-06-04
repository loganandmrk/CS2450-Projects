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

if __name__ == "__main__":
    main()