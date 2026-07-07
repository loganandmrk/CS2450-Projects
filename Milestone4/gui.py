from fileinput import filename
import sys
import tkinter as tk
from tkinter import filedialog
from tkinter import simpledialog
from tkinter import colorchooser
from memory import Memory
from pathlib import Path

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
        root.grid_columnconfigure(3, weight=1)
        root.grid_rowconfigure(0, weight=0)
        root.grid_rowconfigure(1, weight=0)
        root.grid_rowconfigure(2, weight=1)
        root.grid_rowconfigure(3, weight=0)

        

        # control buttons (row 0)
        self.btn_load = tk.Button(root, text="Load File", command=self.load_file)
        self.btn_load.grid(row=0, column=0, padx=25, pady=25, sticky=tk.NSEW)

        self.btn_run = tk.Button(root, text="Run", command=self.run_program)
        self.btn_run.grid(row=0, column=2, padx=25, pady=25, sticky=tk.NSEW)

        self.btn_reset = tk.Button(root, text="Reset", command=self.reset)
        self.btn_reset.grid(row=0, column=1, padx=25, pady=25, sticky=tk.NSEW)

        # output label and text (rows 1-2)
        tk.Label(root, text="Output:").grid(row=1, column=0, padx=5, pady=2, sticky=tk.W)
        self.output_text = tk.Text(root, height=15, width=50)
        self.output_text.grid(row=2, column=0, columnspan=4, padx=5, pady=5, sticky=tk.NSEW)

        self.btn_theme = tk.Button(root, text="Change Colors", command=self.change_colors)
        self.btn_theme.grid(row=0, column=3, padx=25, pady=25, sticky=tk.NSEW)

        default_primary = "#4C721D"
        default_secondary = "#FFFFFF"
        self.apply_theme(default_primary, default_secondary)

    def change_colors(self):
        primary_color = colorchooser.askcolor(title="Choose primary color")[1]
        if not primary_color:
            return

        secondary_color = colorchooser.askcolor(title="Choose secondary color")[1]
        if not secondary_color:
            return

        self.apply_theme(primary_color, secondary_color)

    def apply_theme(self, primary_color, secondary_color):
        self.root.configure(bg=primary_color)
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Button):
                widget.configure(bg=secondary_color, fg="#000000", 
                                 activebackground=primary_color, activeforeground=secondary_color)
            elif isinstance(widget, tk.Label):
                widget.configure(bg=secondary_color, fg=primary_color)
            elif isinstance(widget, tk.Text):
                widget.configure(bg=secondary_color, fg=primary_color, insertbackground=primary_color)

    def load_file(self):
        try:
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
                        index += 1
                    self.log_output(f"Loaded {file_path}")
        except ValueError:
            self.log_output("Invalid file format. Please select a valid UVSim program.")
        except IndexError:
            self.log_output("File contains too long of instruction. Each instruction must be a sign and 4 digits long.")

    def reset(self):
        self.memory = Memory()
        self.program_counter = 0
        self.btn_run.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.log_output("System Reset")
        
    def log_output(self, msg):
        self.output_text.insert(tk.END, msg + "\n")

    def submit_input(self):
        input = simpledialog.askstring("Input", "Please enter an integer:")
        input = int(input)
        return input

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
                    while True:
                        try:
                            self.memory.read(self.memory.read_inst(program_counter)[2], self.submit_input())
                            break
                        except ValueError:
                            self.log_output("Invalid input. Please enter a valid integer.")
                        except OverflowError:
                            self.log_output("Input value is out of range. Please enter a value between -9999 and 9999.")
                case 11:
                    #WRITE
                    try:
                        self.memory.write(self.memory.read_inst(program_counter)[2], self.log_output(self.memory.write(self.memory.read_inst(program_counter)[2])))
                    except ValueError:
                        self.log_output("Invalid memory address. Please check the program for errors.")
                        self.reset()
                case 20:
                    #LOAD
                    try:
                        self.memory.load(self.memory.read_inst(program_counter)[2])
                    except ValueError:
                        self.log_output("Invalid memory address. Please check the program for errors.")
                        self.reset()
                case 21:
                    #STORE
                    try:
                        self.memory.store(self.memory.read_inst(program_counter)[2])
                    except ValueError:
                        self.log_output("Invalid memory address. Please check the program for errors.")
                        self.reset()
                    except OverflowError:
                        self.log_output("Accumulator or input value is out of range.")
                        self.reset()
                case 30:
                    #print(self.memory.read_inst(program_counter)[2])
                    try:
                        self.memory.add(self.memory.read_inst(program_counter)[2])
                    except ValueError:
                        self.log_output("Invalid memory address. Please check the program for errors.")
                        self.reset()
                case 31:
                    try:
                        self.memory.subtract(self.memory.read_inst(program_counter)[2])
                    except ValueError:
                        self.log_output("Invalid memory address. Please check the program for errors.")
                        self.reset()
                case 32:
                    #DIVIDE
                    try:
                        self.memory.divide(self.memory.read_inst(program_counter)[2])
                    except ValueError:
                        self.log_output("Invalid memory address. Please check the program for errors.")
                        self.reset()
                case 33:
                    #MULTIPLY
                    try:
                        self.memory.multiply(self.memory.read_inst(program_counter)[2])
                    except ValueError:
                        self.log_output("Invalid memory address. Please check the program for errors.")
                        self.reset()
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