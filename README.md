
Welcome to using the UVSim developed by Ryan Black, Logan Christiansen, Gerardo Munoz, and Tyler Jenkins!

In order for the UVSim GUI to function please run the following command in your terminal: python main.py

You will need to make sure that your are correctly in the right directory of the most current milestone!
To cd into a file in a command line please enter: cd {file/folder name}.

You can also run the gui by opening the main.py file and clicking run in any python emulator.

Test files are provided for to showcase how the system will work in the testfiles folder.

The Gui consists of 3 different options for the user to select:
1. The "Load File" button accepts a .txt file that has been previously written to execute the instructions provided.
   Once the file is loaded a confirmation message will appear in the output box. If no file is entered a message will appear.
2. The "Reset" button will clear the output box and then clear any memory and functions done. It will print a message when the system is successfully reset.
3. The "Run" button will begin the execution of the file loaded.

If the program that is running on the UVSim requires a user input it will ask for a value from the user. 
Valid inputs would be integers from 9999 to -9999. If the user wishes to select a negative number they will need to type a '-' before the number.

Outputs will be posted to the output box as well as any error messages.

<img width="504" height="731" alt="Phase1GUI Design" src="https://github.com/loganandmrk/CS2450-Projects/blob/main/example.png.png" />

In order to fully understand the functions of the program we have outlined what each instruction does:
I/O operation:
    READ = 10 Read a word from the keyboard into a specific location in memory.
    WRITE = 11 Write a word from a specific location in memory to screen.

Load/store operations:
    LOAD = 20 Load a word from a specific location in memory into the accumulator.
    STORE = 21 Store a word from the accumulator into a specific location in memory.

Arithmetic operation:
    ADD = 30 Add a word from a specific location in memory to the word in the accumulator (leave the result in the accumulator)
    SUBTRACT = 31 Subtract a word from a specific location in memory from the word in the accumulator (leave the result in the accumulator)
    DIVIDE = 32 Divide the word in the accumulator by a word from a specific location in memory (leave the result in the accumulator).
    MULTIPLY = 33 multiply a word from a specific location in memory to the word in the accumulator (leave the result in the accumulator).

Control operation:
    BRANCH = 40 Branch to a specific location in memory
    BRANCHNEG = 41 Branch to a specific location in memory if the accumulator is negative.
    BRANCHZERO = 42 Branch to a specific location in memory if the accumulator is zero.
    HALT = 43 Stop the program

A good example file that adds two inputs together would look like this:
    +1007
    +1008
    +2007
    +3008
    +2109
    +1109
    +4300
    +0000
    +0000
    +0000

To run unit tests please use this command when in the most current milestone directory: python -m unittest unit_tests

Each program must contain a +4300 instruction to properly terminate the program.

That should be everything, thanks for taking a look at our program!
