
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import simpledialog
from memory import Memory, decode_instruction, describe_word, format_word, parse_word
 
 
class UVSimGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("UVSim Emulator")
        self.root.geometry("640x820")
 
        self.memory = Memory()
        self.program_counter = 0
        self.clipboard = []
 
        root.grid_columnconfigure(0, weight=1)
        root.grid_columnconfigure(1, weight=1)
        root.grid_columnconfigure(2, weight=1)
        root.grid_columnconfigure(3, weight=0)
        root.grid_rowconfigure(0, weight=0)
        root.grid_rowconfigure(1, weight=0)
        root.grid_rowconfigure(2, weight=3)
        root.grid_rowconfigure(3, weight=0)
        root.grid_rowconfigure(4, weight=0)
        root.grid_rowconfigure(5, weight=1)
 
        self.btn_load = tk.Button(root, text="Load File", command=self.load_file)
        self.btn_load.grid(row=0, column=0, padx=20, pady=15, sticky=tk.NSEW)
 
        self.btn_reset = tk.Button(root, text="Reset", command=self.reset)
        self.btn_reset.grid(row=0, column=1, padx=20, pady=15, sticky=tk.NSEW)
 
        self.btn_run = tk.Button(root, text="Run", command=self.run_program)
        self.btn_run.grid(row=0, column=2, padx=20, pady=15, sticky=tk.NSEW)
 
        self.btn_edit = tk.Button(root, text="Add / Edit Slot", command=self.edit_selected_slot)
        self.btn_edit.grid(row=1, column=0, padx=5, pady=5, sticky=tk.NSEW)
 
        self.btn_delete = tk.Button(root, text="Delete", command=self.delete_selected_slots)
        self.btn_delete.grid(row=1, column=1, padx=5, pady=5, sticky=tk.NSEW)
 
        editor_btn_frame = tk.Frame(root)
        editor_btn_frame.grid(row=1, column=2, padx=5, pady=5, sticky=tk.NSEW)
        self.btn_cut = tk.Button(editor_btn_frame, text="Cut", command=self.cut_selected_slots)
        self.btn_cut.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.btn_copy = tk.Button(editor_btn_frame, text="Copy", command=self.copy_selected_slots)
        self.btn_copy.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.btn_paste = tk.Button(editor_btn_frame, text="Paste", command=self.paste_into_selected_slot)
        self.btn_paste.pack(side=tk.LEFT, expand=True, fill=tk.X)
 
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
        self.editor_tree.grid(row=2, column=0, columnspan=3, padx=(5, 0), pady=5, sticky=tk.NSEW)
 
        editor_scrollbar = tk.Scrollbar(root, orient="vertical", command=self.editor_tree.yview)
        self.editor_tree.configure(yscrollcommand=editor_scrollbar.set)
        editor_scrollbar.grid(row=2, column=3, pady=5, sticky=tk.NS)
 
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
            text="Double-click a row to add/edit it. Select rows for Cut/Copy/Paste/Delete.",
            fg="gray",
        ).grid(row=3, column=0, columnspan=4, padx=5, sticky=tk.W)
 
        tk.Label(root, text="Output:").grid(row=4, column=0, padx=5, pady=2, sticky=tk.W)
        self.output_text = tk.Text(root, height=10, width=50)
        self.output_text.grid(row=5, column=0, columnspan=4, padx=5, pady=5, sticky=tk.NSEW)
 
        self.refresh_editor()
 
    def refresh_editor(self, keep_selection=None):
        selection_to_restore = (
            keep_selection if keep_selection is not None else self.editor_tree.selection()
        )
        self.editor_tree.delete(*self.editor_tree.get_children())
        for i in range(self.memory.memory_size):
            addr = f"{i:02d}"
            value = self.memory.read_inst(addr)
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
            self.memory.write_inst(addr, value)
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
 
    def load_file(self):
        file_path = filedialog.askopenfilename(
            title="Select UVSim Program", filetypes=[("Text Files", "*.txt")]
        )
        if file_path:
            self._load_program_from_path(file_path)
 
    def load_file_from_path(self, file_path):
        self._load_program_from_path(file_path)
 
    def _load_program_from_path(self, file_path):
        try:
            with open(file_path, "r") as file:
                raw_lines = file.read().splitlines()
        except OSError as e:
            self.log_output(f"Could not open file: {e}")
            return
 
        while raw_lines and raw_lines[-1].strip() == "":
            raw_lines.pop()
 
        self.memory = Memory()
        self.clipboard = []
 
        loaded_count = 0
        overflow_count = 0
        line_errors = []
 
        for index, line in enumerate(raw_lines):
            if index >= self.memory.memory_size:
                overflow_count += 1
                continue
            addr = f"{index:02d}"
            try:
                value = parse_word(line)
            except (ValueError, OverflowError) as e:
                line_errors.append(f"Line {index + 1} (address {addr}): {e}")
                continue
            self.memory.write_inst(addr, value)
            loaded_count += 1
 
        self.log_output(f"Loaded {file_path}")
        self.log_output(f"{loaded_count} entries loaded successfully.")
        if overflow_count:
            self.log_output(
                f"{overflow_count} line(s) exceeded the 100-address limit (00-99) "
                f"and were not loaded."
            )
        if line_errors:
            self.log_output(
                f"{len(line_errors)} line(s) had errors and were left empty "
                f"-- fix them in the editor above, then Run:"
            )
            for msg in line_errors:
                self.log_output("  " + msg)
 
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
        self.output_text.see(tk.END)
 
    def submit_input(self):
        user_input = simpledialog.askstring("Input", "Please enter an integer:")
        if user_input is None:
            self.log_output("Input cancelled. Please restart the program and enter a valid integer.")
            return None
        try:
            return int(user_input)
        except ValueError:
            self.log_output("Invalid input. Please enter a valid integer.")
            return None
 
    def run_program(self):
        program_counter = 0
        run = True
 
        while run:
            if program_counter >= self.memory.memory_size:
                self.log_output("Program ran past the last address without a HALT instruction.")
                break
 
            raw_value = self.memory.read_inst(program_counter)
            if raw_value is None:
                self.log_output(f"Address {program_counter:02d} is empty. Halting.")
                break
 
            opcode, operand = decode_instruction(raw_value)
 
            match opcode:
                case 10:
                    while True:
                        try:
                            user_input = self.submit_input()
                            if user_input is None:
                                run = False
                                break
                            self.memory.read(operand, user_input)
                            break
                        except ValueError:
                            self.log_output("Invalid input. Please enter a valid integer.")
                        except OverflowError:
                            self.log_output(
                                "Input value is out of range. Please enter a value between -9999 and 9999."
                            )
                    if not run:
                        break
                case 11:
                    try:
                        value = self.memory.write(operand)
                        self.log_output(value)
                    except ValueError as e:
                        self.log_output(f"{e}. Please check the program for errors.")
                        self.reset()
                        return
                case 20:
                    try:
                        self.memory.load(operand)
                    except ValueError as e:
                        self.log_output(f"{e}. Please check the program for errors.")
                        self.reset()
                        return
                case 21:
                    try:
                        self.memory.store(operand)
                    except ValueError as e:
                        self.log_output(f"{e}. Please check the program for errors.")
                        self.reset()
                        return
                    except OverflowError:
                        self.log_output("Accumulator value is out of range.")
                        self.reset()
                        return
                case 30:
                    try:
                        self.memory.add(operand)
                    except ValueError as e:
                        self.log_output(f"{e}. Please check the program for errors.")
                        self.reset()
                        return
                case 31:
                    try:
                        self.memory.subtract(operand)
                    except ValueError as e:
                        self.log_output(f"{e}. Please check the program for errors.")
                        self.reset()
                        return
                case 32:
                    try:
                        self.memory.divide(operand)
                    except ValueError as e:
                        self.log_output(f"{e}. Please check the program for errors.")
                        self.reset()
                        return
                case 33:
                    try:
                        self.memory.multiply(operand)
                    except ValueError as e:
                        self.log_output(f"{e}. Please check the program for errors.")
                        self.reset()
                        return
                case 40:
                    program_counter = int(operand)
                    continue
                case 41:
                    if self.memory.acumulator < 0:
                        program_counter = int(operand)
                        continue
                case 42:
                    if self.memory.acumulator == 0:
                        program_counter = int(operand)
                        continue
                case 43:
                    run = False
                    break
                case _:
                    self.log_output(
                        f"Address {program_counter:02d} contains {format_word(raw_value)}, "
                        f"which is not a recognized instruction. Halting."
                    )
                    run = False
                    break
            program_counter += 1
 
        self.refresh_editor()