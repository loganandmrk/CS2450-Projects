from fileinput import filename
from logging import root
import sys
import tkinter as tk
from tkinter import filedialog
from tkinter import simpledialog
from tkinter import colorchooser
from tkinter import ttk
from memory import Memory
from pathlib import Path
from memory import Memory, decode_instruction, describe_word, format_word, parse_word

class UVSimGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("UVSim Emulator")
        self.root.state("zoomed")
        
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
        root.grid_rowconfigure(2, weight=0)
        root.grid_rowconfigure(3, weight=1)
        root.grid_rowconfigure(4, weight=0)

        # control buttons (row 0)
        self.btn_load = tk.Button(root, text="Load File", command=self.load_file)
        self.btn_load.grid(row=0, column=0, padx=50, pady=25, sticky=tk.NSEW)

        self.btn_run = tk.Button(root, text="Run", command=self.run_program)
        self.btn_run.grid(row=0, column=2, padx=50, pady=25, sticky=tk.NSEW)

        self.btn_edit = tk.Button(root, text="Add / Edit Slot", command=self.edit_selected_slot)
        self.btn_edit.grid(row=1, column=0, padx=50, pady=25, sticky=tk.NSEW)
 
        self.btn_delete = tk.Button(root, text="Delete", command=self.delete_selected_slots)
        self.btn_delete.grid(row=1, column=1, padx=50, pady=25, sticky=tk.NSEW)

        self.btn_reset = tk.Button(root, text="Reset", command=self.reset)
        self.btn_reset.grid(row=0, column=1, padx=50, pady=25, sticky=tk.NSEW)

        # output label and text (rows 1-2)
        self.output_text = tk.Text(root, height=15, width=50)
        self.output_text.grid(row=3, column=0, columnspan=4, padx=5, pady=5, sticky=tk.NSEW)

        editor_btn_frame = tk.Frame(root)
        editor_btn_frame.grid(row=1, column=2, padx=50, pady=25, sticky=tk.NSEW)
        self.btn_cut = tk.Button(editor_btn_frame, text="Cut", command=self.cut_selected_slots)
        self.btn_cut.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.btn_copy = tk.Button(editor_btn_frame, text="Copy", command=self.copy_selected_slots)
        self.btn_copy.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.btn_paste = tk.Button(editor_btn_frame, text="Paste", command=self.paste_into_selected_slot)
        self.btn_paste.pack(side=tk.LEFT, expand=True, fill=tk.X)

        save_btn_frame = tk.Frame(root)
        save_btn_frame.grid(row=1, column=3, padx=50, pady=25, sticky=tk.NSEW)
        self.btn_save = tk.Button(save_btn_frame, text="Save", command=self.save_file)
        self.btn_save.pack(side=tk.LEFT, expand=True, fill=tk.X)

        columns = ("address", "value", "meaning")
        self.editor_tree = ttk.Treeview(
            root, columns=columns, show="headings", selectmode="extended"
        )
        self.editor_tree.heading("address", text="Address")
        self.editor_tree.heading("value", text="Value")
        self.editor_tree.heading("meaning", text="Meaning")
        self.editor_tree.column("address", width=70, anchor=tk.CENTER, stretch=False)
        self.editor_tree.column("value", width=90, anchor=tk.CENTER, stretch=False)
        self.editor_tree.column("meaning", width=260, anchor=tk.W)
        self.editor_tree.grid(row=3, column=0, columnspan=3, padx=(5, 0), pady=5, sticky=tk.NSEW)
 
        editor_scrollbar = tk.Scrollbar(root, orient="vertical", command=self.editor_tree.yview)
        self.editor_tree.configure(yscrollcommand=editor_scrollbar.set)
        editor_scrollbar.grid(row=3, column=3, pady=5, sticky=tk.NS)
 
        self.editor_tree.bind("<Double-1>", lambda event: self.edit_selected_slot())
        self.editor_tree.bind("<Delete>", lambda event: self.delete_selected_slots())
        self.editor_tree.bind("<BackSpace>", lambda event: self.delete_selected_slots())
        for seq in ("<Control-x>", "<Command-x>"):
            self.editor_tree.bind(seq, lambda event: self.cut_selected_slots())
        for seq in ("<Control-c>", "<Command-c>"):
            self.editor_tree.bind(seq, lambda event: self.copy_selected_slots())
        for seq in ("<Control-v>", "<Command-v>"):
            self.editor_tree.bind(seq, lambda event: self.paste_into_selected_slot())
 
        tk.Label(
            root,
            text="Memory will show up here. Double-click a row to add/edit it. Select rows for Cut/Copy/Paste/Delete.",
            fg="gray",
        ).grid(row=2, column=0, columnspan=4, padx=5, sticky=tk.W)
 
        tk.Label(root, text="Output:").grid(row=4, column=0, padx=5, pady=2, sticky=tk.W)
        self.output_text = tk.Text(root, height=10, width=50)
        self.output_text.grid(row=5, column=0, columnspan=4, padx=5, pady=5, sticky=tk.NSEW)
 
        self.refresh_editor()

        self.btn_reset = tk.Button(root, text="Change Theme", command=self.change_colors)
        self.btn_reset.grid(row=0, column=3, padx=50, pady=25, sticky=tk.NSEW)

        default_primary = "#4C721D"
        default_secondary = "#FFFFFF"
        self.apply_theme(default_primary, default_secondary)
        self.log_output("Welcome to UVSim Emulator! Please load a program to begin.")

    def refresh_editor(self, keep_selection=None):
        selection_to_restore = (
            keep_selection if keep_selection is not None else self.editor_tree.selection()
        )
        self.editor_tree.delete(*self.editor_tree.get_children())
        for i in range(self.memory.memory_size):
            addr = f"{i:02d}"
            value = self.memory.read_inst(addr)
            if isinstance(value, list):
                value = value[4]
            value = int(value) if value is not None else None
            display_value = format_word(value) if value is not None else ""
            meaning = describe_word(value)
            self.editor_tree.insert("", tk.END, iid=addr, values=(addr, display_value, meaning))
        valid_selection = [a for a in selection_to_restore if self.editor_tree.exists(a)]
        if valid_selection:
            self.editor_tree.selection_set(valid_selection)

    def _selected_addresses(self):
        return list(self.editor_tree.selection())
 
    def edit_selected_slot(self):
        selected = self._selected_addresses()
        if len(selected) != 1:
            self.log_output("Select exactly one address to add or edit.")
            return
        addr = selected[0]
        current = self.memory.read_inst(addr)
        if isinstance(current, list):
            current = current[4]
        current = int(current) if current is not None else None
        current_str = format_word(current) if current is not None else ""
        new_value_str = simpledialog.askstring(
            "Add / Edit Slot",
            f"Enter a value for address {addr} (-9999 to 9999).\n"
            f"Leave blank to clear this address.",
            initialvalue=current_str,
        )
        if new_value_str is None:
            return
        if new_value_str.strip() == "":
            self.memory.write_inst(addr, None)
            self.log_output(f"Cleared address {addr}.")
        else:
            try:
                value = parse_word(new_value_str)
            except (ValueError, OverflowError) as e:
                self.log_output(f"Could not set address {addr}: {e}")
                return
            #get the sign, instruction, memory location, value, and full word to store into memory as a list.
            if value >= 0:
                sign = "+"
            else:
                sign = "-"
            instruction = int(str(value)[:2])
            memory_loc = str(value)[2:4]
            line = str(sign + str(value).zfill(4))
            self.memory.write_inst(addr, [sign, int(instruction), str(memory_loc), int(value), line])
            self.log_output(f"Set address {addr} to {format_word(value)}.")
        self.refresh_editor(keep_selection=[addr])
 
    def delete_selected_slots(self):
        selected = self._selected_addresses()
        if not selected:
            self.log_output("Select one or more addresses to delete.")
            return
        for addr in selected:
            self.memory.write_inst(addr, None)
        self.log_output(f"Cleared {len(selected)} address(es): {', '.join(selected)}.")
        self.refresh_editor(keep_selection=selected)
 
    def cut_selected_slots(self):
        selected = self._selected_addresses()
        if not selected:
            self.log_output("Select one or more addresses to cut.")
            return
        self.clipboard = [self.memory.read_inst(addr) for addr in selected]
        for addr in selected:
            self.memory.write_inst(addr, None)
        self.log_output(f"Cut {len(selected)} entry(ies) to the clipboard.")
        self.refresh_editor()
 
    def copy_selected_slots(self):
        selected = self._selected_addresses()
        if not selected:
            self.log_output("Select one or more addresses to copy.")
            return
        self.clipboard = [self.memory.read_inst(addr) for addr in selected]
        self.log_output(f"Copied {len(selected)} entry(ies) to the clipboard.")
 
    def paste_into_selected_slot(self):
        if not self.clipboard:
            self.log_output("Clipboard is empty. Cut or copy something first.")
            return
        selected = self._selected_addresses()
        if len(selected) != 1:
            self.log_output("Select exactly one address to paste starting at.")
            return
        start = int(selected[0])
        fits = min(len(self.clipboard), self.memory.memory_size - start)
        for offset in range(fits):
            addr = f"{start + offset:02d}"
            self.memory.write_inst(addr, self.clipboard[offset])
        skipped = len(self.clipboard) - fits
        if skipped > 0:
            self.log_output(
                f"Pasted {fits} of {len(self.clipboard)} entries starting at address "
                f"{selected[0]}. {skipped} entry(ies) went past address 99 and were not pasted."
            )
        else:
            self.log_output(f"Pasted {fits} entry(ies) starting at address {selected[0]}.")
        self.refresh_editor()
    
    def clear_editor(self):
        for i in range(self.memory.memory_size):
            self.memory.write_inst(i, None)
        self.refresh_editor()

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
        self.refresh_editor()

    def reset(self):
        self.memory = Memory()
        self.program_counter = 0
        self.btn_run.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.log_output("System Reset")
        self.refresh_editor()
        
    def log_output(self, msg):
        self.output_text.insert(tk.END, msg + "\n")

    def submit_input(self):
        user_input = simpledialog.askstring("Input", "Please enter an integer:", parent=self.root)
        if user_input is None:
            self.log_output("Input cancelled. Please restart the program and enter a valid integer.")
            return None
        try:
            return int(user_input)
        except ValueError:
            self.log_output("Invalid input. Please enter a valid integer.")
            return None

    def save_file(self):
        file_path = filedialog.asksaveasfilename(title="Save UVSim Program", defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if file_path:
            with open(file_path, 'w') as file:
                for i in range(self.memory.memory_size):
                    value = self.memory.read_inst(i)
                    if isinstance(value, list):
                        value = value[4]
                    if describe_word(value) != "DATA" and value is not None:
                        file.write(f"{value}\n")
            self.log_output(f"Program saved to {file_path}")

    def run_program(self):
        program_counter = 0
        run = True
        
        while run:
            try:
                opcode = int(self.memory.read_inst(program_counter)[1])
            except (ValueError, TypeError):
                self.log_output(f"Data may be writing over instructions. Please check program for errors.")
                break
            if program_counter > 99:
                opcode=43
            match opcode:
                case 10:
                    #READ
                    while True:
                        try:
                            user_input = self.submit_input()
                            if user_input is None:
                                run = False
                                break
                            self.memory.read(self.memory.read_inst(program_counter)[2], user_input)
                            break
                        except ValueError:
                            self.log_output("Invalid input. Please enter a valid integer.")
                        except OverflowError:
                            self.log_output("Input value is out of range. Please enter a value between -9999 and 9999.")
                    if not run:
                        break
                case 11:
                    #WRITE
                    try:
                        value = self.memory.write(self.memory.read_inst(program_counter)[2])
                        self.log_output(value)
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
        self.refresh_editor()