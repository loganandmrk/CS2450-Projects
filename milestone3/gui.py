from fileinput import filename
import sys
import tkinter as tk
from tkinter import filedialog
from tkinter import simpledialog
from memory import Memory

class UVSimGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("UVSim Emulator")
        self.root.geometry("500x700")
        
        self.memory = Memory()
        self.program_counter = 0
        self.waiting_for_input = False
        self.input_address = None
        
        # configure grid: three columns (buttons, output area, submit)
        root.grid_columnconfigure(0, weight=1)
        root.grid_columnconfigure(1, weight=1)
        root.grid_columnconfigure(2, weight=1)
        root.grid_rowconfigure(0, weight=0)
        root.grid_rowconfigure(1, weight=0)
        root.grid_rowconfigure(2, weight=1)
        root.grid_rowconfigure(3, weight=0)

        # control buttons (row 0)
        self.btn_load = tk.Button(root, text="Load File", command=self.load_file)
        self.btn_load.grid(row=0, column=0, padx=50, pady=25, sticky=tk.NSEW)

        self.btn_run = tk.Button(root, text="Run", command=self.run_program)
        self.btn_run.grid(row=0, column=2, padx=50, pady=25, sticky=tk.NSEW)

        self.btn_reset = tk.Button(root, text="Reset", command=self.reset)
        self.btn_reset.grid(row=0, column=1, padx=50, pady=25, sticky=tk.NSEW)

        # output label and text (rows 1-2)
        tk.Label(root, text="Output:").grid(row=1, column=0, padx=5, pady=2, sticky=tk.W)
        self.output_text = tk.Text(root, height=15, width=50)
        self.output_text.grid(row=2, column=0, columnspan=3, padx=5, pady=5, sticky=tk.NSEW)

        # input row (below output)
        tk.Label(root, text="Please enter Input here:").grid(row=3, column=0, padx=5, pady=2, sticky=tk.EW)
        self.input_entry = tk.Entry(root)
        self.input_entry.grid(row=3, column=1, padx=5, pady=2, sticky=tk.EW)

        self.btn_submit = tk.Button(root, text="Submit Input", command=self.submit_input, state=tk.DISABLED)
        self.btn_submit.grid(row=3, column=2, padx=5, pady=2, sticky=tk.EW)

    def load_file(self):
        file_path = filedialog.askopenfilename(title="Select UVSim Program", filetypes=[("Text Files", "*.txt")])
        if file_path:
            with open(file_path, 'r') as file:
                lines = file.read().splitlines()
                index = 0
                for line in lines:
                    sign = line[0] #sign of the instruction, either + or -
                    instruction = line[1:3] #the 2 digit instruction of the program
                    memory_loc = line[3:5] #the 2 digit memory location operations should be performed on
                    value = line[1:5] #full integer

        #writes memory with index as key number, then stores parsed info into memory of key using a list.
                    self.memory.write_inst(index, [sign, int(instruction), str(memory_loc), int(value), line])
                    print(self.memory.read_inst(index))
                    index += 1

    def load_file_from_path(self, filename):
        try:
            with open(filename, 'r') as file:
                lines = file.read().splitlines()
                for index, line in enumerate(lines):
                    if not line: continue
                    sign = line[0]
                    instruction = line[1:3]
                    memory_loc = line[3:5]
                    value = line[1:5]
                    self.memory.write_inst(index, [sign, int(instruction), str(memory_loc), int(value), line])
            print(f"Loaded {filename}")
        except:
            print(f"No File Found")  

    def reset(self):
        self.memory = Memory()
        self.program_counter = 0
        self.waiting = False
        
    def log_output(self, msg):
        self.output_text.insert(tk.END, msg + "\n")

    def submit_input(self):
        input = simpledialog.askstring("Input", "Please enter a value:")
        if input:
            print("user entered: " + input)

    def run_program(self):
        program_counter = 0
        run = True
        
        while run:
            #print(f"Current PC: {program_counter}, Read Result: {memory.read_inst(program_counter)} Accumulator: {memory.acumulator}")
            #print(memory.acumulator)
            opcode = int(self.memory.read_inst(program_counter)[1])
            if program_counter > 99:
                opcode=43
            match opcode:
                case 10:
                    #READ
                    self.memory.read(self.memory.read_inst(program_counter)[2], self.submit_input())
                case 11:
                    #WRITE
                    self.memory.write(self.memory.read_inst(program_counter)[2], self.log_output())
                case 20:
                    #LOAD
                    self.memory.load(self.memory.read_inst(program_counter)[2])
                case 21:
                    #STORE
                    self.memory.store(self.memory.read_inst(program_counter)[2])
                case 30:
                    #print(self.memory.read_inst(program_counter)[2])
                    self.memory.add(self.memory.read_inst(program_counter)[2])
                case 31:
                    self.memory.subtract(self.memory.read_inst(program_counter)[2])
                case 32:
                    #DIVIDE
                    self.memory.divide(self.memory.read_inst(program_counter)[2])
                case 33:
                    #MULTIPLY
                    self.memory.multiply(self.memory.read_inst(program_counter)[2])
                case 40:
                    #BRANCH
                    program_counter = int(self.memory.read_inst(program_counter)[2])
                    continue
                    
                case 41:
                    #BRANCHNEG
                    if self.memory.acumulator < 0:
                        program_counter = int(self.memory.read_inst(program_counter)[2])
                        continue 
                    
                case 42:
                    #BRANCHZERO
                    if self.memory.acumulator == 0:
                        program_counter = int(self.memory.read_inst(program_counter)[2])
                        continue
                    
                case 43:
                    #HALT
                    run = False
                    break
                    
                case _:
                    print("Invalid instruction")
            program_counter += 1


"""def main():
    root = tk.Tk()
    app = UVSimGUI(root)
    
    if len(sys.argv) == 2:
        app.load_file_from_path(sys.argv[1])
    elif len(sys.argv) > 2:
        print("Too many arguments presented. Launching GUI empty.")
        
    root.mainloop()

if __name__ == "__main__":
    main()"""