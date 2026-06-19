import sys
import tkinter as tk
from tkinter import filedialog
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
        pass
    def load_file_from_path(self, filename):
        pass

    def reset(self):
        pass
        
    def log_output(self, msg):
        pass

    def submit_input(self):
        pass

    def run_program(self):
        pass

def main():
    root = tk.Tk()
    app = UVSimGUI(root)
    
    if len(sys.argv) == 2:
        app.load_file_from_path(sys.argv[1])
    elif len(sys.argv) > 2:
        print("Too many arguments presented. Launching GUI empty.")
        
    root.mainloop()

if __name__ == "__main__":
    main()