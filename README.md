Welcome to using the UVSim developed by Ryan Black, Logan Christiansen, Gerardo Munoz, and Tyler Jenkins!

In order for the product to function are are required to run the program from the command line.
Make sure you are in the working directory and run it by using your python interpreter (usually python or py installed serpately)
Use this bit of code as a template:
```bash
python Milestone2/main.py Milestone2/<filename>
```
"filename" should be replaced by your test file. We have provided test files labeled "Test1.txt" through "Test5.txt" to verify the program is working.

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

To run unit tests please use this command: python -m unittest unit_tests

Each program must contain a +4300 instruction to properly terminate the program.

That should be everything, thanks for taking a look at our program!
