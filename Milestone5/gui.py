from fileinput import filename
from logging import root
import sys
import csv
import tkinter as tk
from tkinter import filedialog
from tkinter import simpledialog
from tkinter import colorchooser
from tkinter import ttk

from memory import Memory, decode_instruction, describe_word, format_word, parse_word


class UVSimTab:
    """
    Holds everything that belongs to a single open file: its own Memory
    (registers/accumulator), its own clipboard, and its own editor/output
    widgets. Each tab is fully independent of every other tab, so multiple
    files can be open, edited, and executed in any order without one
    file's state leaking into another's.
    """

    _untitled_counter = itertools.count(1)

    def __init__(self, parent, notebook, file_path=None):
        self.parent = parent
        self.notebook = notebook
        self.memory = Memory()
        self.clipboard = None
        self.file_path = file_path

        if file_path:
            self.title = file_path.split("/")[-1].split("\\")[-1]
        else:
            self.title = f"Untitled-{next(UVSimTab._untitled_counter)}"

        parent.grid_columnconfigure(0, weight=1)
        parent.grid_columnconfigure(1, weight=1)
        parent.grid_columnconfigure(2, weight=1)
        parent.grid_columnconfigure(3, weight=1)
        parent.grid_rowconfigure(3, weight=1)
        parent.grid_rowconfigure(5, weight=1)

        # control buttons (row 0)
        self.btn_load = tk.Button(parent, text="Load File", command=self.load_file)
        self.btn_load.grid(row=0, column=0, padx=50, pady=25, sticky=tk.NSEW)

        self.btn_run = tk.Button(parent, text="Run", command=self.run_program)
        self.btn_run.grid(row=0, column=2, padx=50, pady=25, sticky=tk.NSEW)

        self.btn_edit = tk.Button(parent, text="Add / Edit Slot", command=self.edit_selected_slot)
        self.btn_edit.grid(row=1, column=0, padx=50, pady=25, sticky=tk.NSEW)

        self.btn_delete = tk.Button(parent, text="Delete", command=self.delete_selected_slots)
        self.btn_delete.grid(row=1, column=1, padx=50, pady=25, sticky=tk.NSEW)

        self.btn_reset = tk.Button(parent, text="Reset", command=self.reset)
        self.btn_reset.grid(row=0, column=1, padx=50, pady=25, sticky=tk.NSEW)

        editor_btn_frame = tk.Frame(parent)
        editor_btn_frame.grid(row=1, column=2, padx=50, pady=25, sticky=tk.NSEW)
        self.btn_cut = tk.Button(editor_btn_frame, text="Cut", command=self.cut_selected_slots)
        self.btn_cut.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.btn_copy = tk.Button(editor_btn_frame, text="Copy", command=self.copy_selected_slots)
        self.btn_copy.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.btn_paste = tk.Button(editor_btn_frame, text="Paste", command=self.paste_into_selected_slot)
        self.btn_paste.pack(side=tk.LEFT, expand=True, fill=tk.X)

        save_btn_frame = tk.Frame(parent)
        save_btn_frame.grid(row=1, column=3, padx=50, pady=25, sticky=tk.NSEW)
        self.btn_save = tk.Button(save_btn_frame, text="Save", command=self.save_file)
        self.btn_save.pack(side=tk.LEFT, expand=True, fill=tk.X)

        tk.Label(
            parent,
            text="Memory will show up here. Double-click a row to add/edit it. Select rows for Cut/Copy/Paste/Delete.",
            fg="gray",
        ).grid(row=2, column=0, columnspan=4, padx=5, sticky=tk.W)

        columns = ("address", "value", "meaning")
        self.editor_tree = ttk.Treeview(
            parent,
            columns=columns,
            show="headings",
            selectmode="extended",
            style="UVSim.Treeview",
        )
        self.editor_tree.heading("address", text="Address")
        self.editor_tree.heading("value", text="Value")
        self.editor_tree.heading("meaning", text="Meaning")
        self.editor_tree.column("address", width=70, anchor=tk.CENTER, stretch=False)
        self.editor_tree.column("value", width=90, anchor=tk.CENTER, stretch=False)
        self.editor_tree.column("meaning", width=260, anchor=tk.W)
        self.editor_tree.grid(row=3, column=0, columnspan=3, padx=(5, 0), pady=5, sticky=tk.NSEW)

        editor_scrollbar = tk.Scrollbar(parent, orient="vertical", command=self.editor_tree.yview)
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

        tk.Label(parent, text="Output:").grid(row=4, column=0, padx=5, pady=2, sticky=tk.W)
        self.output_text = tk.Text(parent, height=10, width=50)
        self.output_text.grid(row=5, column=0, columnspan=4, padx=5, pady=5, sticky=tk.NSEW)

        self.refresh_editor()

        if file_path:
            self._load_file_from_path(file_path)
        else:
            self.log_output("Welcome to UVSim Emulator! Please load a program to begin.")

    # ------------------------------------------------------------------
    # editor / memory view
    # ------------------------------------------------------------------

    def refresh_editor(self, keep_selection=None):
        selection_to_restore = (
            keep_selection if keep_selection is not None else self.editor_tree.selection()
        )
        self.editor_tree.delete(*self.editor_tree.get_children())
        for i in range(self.memory.memory_size):
            addr = f"{i:03d}"
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
            addr = f"{start + offset:03d}"
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

    # ------------------------------------------------------------------
    # file I/O
    # ------------------------------------------------------------------

    def _load_program_lines(self, lines):
        self.memory = Memory()
        index = 0
        for line in lines:
            if index >= self.memory.memory_size:
                break
            self.memory.write_inst(index, int(line))
            index += 1

    def _load_file_from_path(self, file_path):
        try:
            file_path = filedialog.askopenfilename(title="Select UVSim Program", filetypes=[("Text Files", "*.txt"), ("CSV Files", "*.csv")])
            if file_path:
                with open(file_path, 'r') as file:
                    if file_path.endswith('.csv'):
                        lines = []
                        reader = csv.reader(file)
                        for row in reader:
                            lines.append(row[1])
                    else:
                        lines = file.read().splitlines()
                self._load_program_lines(lines)
                self.log_output(f"Loaded {file_path}")
        except ValueError:
            self.log_output("Invalid file format. Please select a valid UVSim program.")
        except IndexError:
            self.log_output(
                "File contains too long of instruction. Each instruction must be a sign and 4 digits long."
            )
        except OSError as e:
            self.log_output(f"Could not open file: {e}")
        self.refresh_editor()
        self._sync_tab_label()

    def _sync_tab_label(self):
        """Update this tab's label in the notebook, if it's been added yet."""
        if str(self.parent) in self.notebook.tabs():
            self.notebook.tab(self.parent, text=self.title)

    def load_file(self):
        file_path = filedialog.askopenfilename(
            title="Select UVSim Program", filetypes=[("Text Files", "*.txt")]
        )
        if file_path:
            self._load_file_from_path(file_path)

    def save_file(self):
        file_path = filedialog.asksaveasfilename(
            title="Save UVSim Program", defaultextension=".txt", filetypes=[("Text Files", "*.txt")]
        )
        if file_path:
            with open(file_path, "w") as file:
                for i in range(self.memory.memory_size):
                    value = self.memory.read_inst(i)
                    if isinstance(value, list):
                        value = value[4]
                    if describe_word(value) != "DATA" and value is not None:
                        file.write(f"{value}\n")
            self.file_path = file_path
            self.title = file_path.split("/")[-1].split("\\")[-1]
            self._sync_tab_label()
            self.log_output(f"Program saved to {file_path}")

    def reset(self):
        self.memory = Memory()
        self.clipboard = None
        self.btn_run.config(state=tk.NORMAL)
        self.output_text.delete(1.0, tk.END)
        self.log_output("System Reset")
        self.refresh_editor()

    def log_output(self, msg):
        self.output_text.insert(tk.END, str(msg) + "\n")
        self.output_text.see(tk.END)
        self.parent.update_idletasks()

    def submit_input(self):
        user_input = simpledialog.askstring(
            "Input", "Please enter an integer:", parent=self.parent
        )
        if user_input is None:
            self.log_output("Input cancelled. Please restart the program and enter a valid integer.")
            return None
        try:
            return int(user_input)
        except ValueError:
            self.log_output("Invalid input. Please enter a valid integer.")
            return None

    def save_file(self):
        file_path = filedialog.asksaveasfilename(title="Save UVSim Program", defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if file_path:
            with open(file_path, 'w') as file:
                writer = csv.writer(file)
                for i in range(self.memory.memory_size):
                    try:
                        writer.writerow([f"{i:03d}", f"{self.memory.read_inst(f"{i:03d}"):06d}"])
                    except (ValueError, TypeError):
                        writer.writerow([f"{i:03d}", ""])
            self.log_output(f"Program saved to {file_path}")

    def run_program(self):
        program_counter = 0
        run = True

        while run:
            raw_value = self.memory.read_inst(program_counter)
            if isinstance(raw_value, list):
                raw_value = int(raw_value[4])
            if raw_value is None:
                self.log_output(f"Address {program_counter:03d} is empty. Halting.")
                break
            try:
                opcode, operand = decode_instruction(raw_value)
            except (ValueError, TypeError):
                self.log_output("Data may be writing over instructions. Please check program for errors.")
                break
            if program_counter > 99:
                opcode = 43
            match opcode:
                case 10:
                    # READ
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
                    # WRITE
                    try:
                        value = self.memory.write(operand)
                        self.log_output(value)
                    except ValueError:
                        self.log_output("Invalid memory address. Please check the program for errors.")
                        self.reset()
                        return
                case 20:
                    # LOAD
                    try:
                        self.memory.load(operand)
                    except ValueError:
                        self.log_output("Invalid memory address. Please check the program for errors.")
                        self.reset()
                        return
                case 21:
                    # STORE
                    try:
                        self.memory.store(operand)
                    except ValueError:
                        self.log_output("Invalid memory address. Please check the program for errors.")
                        self.reset()
                        return
                    except OverflowError:
                        self.log_output("Accumulator or input value is out of range.")
                        self.reset()
                        return
                case 30:
                    try:
                        self.memory.add(operand)
                    except ValueError:
                        self.log_output("Invalid memory address. Please check the program for errors.")
                        self.reset()
                        return
                case 31:
                    try:
                        self.memory.subtract(operand)
                    except ValueError:
                        self.log_output("Invalid memory address. Please check the program for errors.")
                        self.reset()
                        return
                case 32:
                    # DIVIDE
                    try:
                        self.memory.divide(operand)
                    except ValueError:
                        self.log_output("Invalid memory address. Please check the program for errors.")
                        self.reset()
                        return
                case 33:
                    # MULTIPLY
                    try:
                        self.memory.multiply(operand)
                    except ValueError:
                        self.log_output("Invalid memory address. Please check the program for errors.")
                        self.reset()
                        return
                case 40:
                    # BRANCH
                    program_counter = int(operand)
                    continue

                case 41:
                    # BRANCHNEG
                    if self.memory.acumulator < 0:
                        program_counter = int(operand)
                        continue

                case 42:
                    # BRANCHZERO
                    if self.memory.acumulator == 0:
                        program_counter = int(operand)
                        continue

                case 43:
                    # HALT
                    run = False
                    break

                case _:
                    self.log_output(
                        f"Address {program_counter:03d} contains {format_word(raw_value)}, "
                        f"which is not a recognized instruction. Halting."
                    )
                    run = False
                    break
            program_counter += 1
        self.refresh_editor()


class UVSimGUI:
    """
    App shell: owns a ttk.Notebook so that any number of files can be open
    at once, each in its own tab, each backed by its own UVSimTab (and
    therefore its own Memory instance). Switching tabs switches which
    file's editor/output/memory you're looking at and acting on; every
    tab remains independently editable and independently executable.
    """

    def __init__(self, root):
        self.root = root
        self.root.title("UVSim Emulator")
        try:
            self.root.state("zoomed")
        except tk.TclError:
            # Some window managers (or headless environments) don't
            # support "zoomed"; just fall back to the default size.
            pass

        self.tabs = {}  # str(frame) -> UVSimTab

        toolbar = tk.Frame(root)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        self.btn_new_tab = tk.Button(toolbar, text="New Tab", command=self.new_blank_tab)
        self.btn_new_tab.pack(side=tk.LEFT, padx=10, pady=5)

        self.btn_open_tab = tk.Button(toolbar, text="Open File in New Tab", command=self.open_file_in_new_tab)
        self.btn_open_tab.pack(side=tk.LEFT, padx=10, pady=5)

        self.btn_close_tab = tk.Button(toolbar, text="Close Tab", command=self.close_current_tab)
        self.btn_close_tab.pack(side=tk.LEFT, padx=10, pady=5)

        self.btn_theme = tk.Button(toolbar, text="Change Theme", command=self.change_colors)
        self.btn_theme.pack(side=tk.LEFT, padx=10, pady=5)

        self.default_primary = "#4C721D"
        self.default_secondary = "#FFFFFF"
        self._theme = (self.default_primary, self.default_secondary)
        self.configure_styles(*self._theme)

        self.notebook = ttk.Notebook(root, style="UVSim.TNotebook")
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.new_blank_tab()

    # ------------------------------------------------------------------
    # tab management
    # ------------------------------------------------------------------

    def current_tab(self):
        tab_id = self.notebook.select()
        if not tab_id:
            return None
        return self.tabs.get(tab_id)

    def open_new_tab(self, file_path=None):
        frame = tk.Frame(self.notebook)
        tab = UVSimTab(frame, self.notebook, file_path=file_path)
        self.notebook.add(frame, text=tab.title)
        self.tabs[str(frame)] = tab
        tab._sync_tab_label()
        self.notebook.select(frame)
        self.root.update_idletasks()
        self.root.after_idle(self.change_theme)
        return tab

    def new_blank_tab(self):
        self.open_new_tab(file_path=None)

    def open_file_in_new_tab(self):
        file_path = filedialog.askopenfilename(
            title="Select UVSim Program", filetypes=[("Text Files", "*.txt")]
        )
        if file_path:
            self.open_new_tab(file_path=file_path)

    def load_file_from_path(self, file_path):
        """Used for opening a file passed in on the command line."""
        return self.open_new_tab(file_path=file_path)

    def close_current_tab(self):
        tab_id = self.notebook.select()
        if not tab_id:
            return
        self.notebook.forget(tab_id)
        self.tabs.pop(tab_id, None)
        if not self.tabs:
            self.new_blank_tab()

    # ------------------------------------------------------------------
    # theming (applies across every open tab)
    # ------------------------------------------------------------------

    def change_colors(self):
        primary_color = colorchooser.askcolor(title="Choose primary color")[1]
        if not primary_color:
            return

        secondary_color = colorchooser.askcolor(title="Choose secondary color")[1]
        if not secondary_color:
            return

        self.apply_theme(primary_color, secondary_color)

    def change_theme(self):
        self.apply_theme(*self._theme)


    def configure_styles(self, primary_color, secondary_color):
        style = ttk.Style(self.root)
        try:
            if "clam" in style.theme_names():
                style.theme_use("clam")
            else:
                style.theme_use(style.theme_use())
        except tk.TclError:
            pass

        style.configure(
            "UVSim.Treeview",
            background=secondary_color,
            fieldbackground=secondary_color,
            foreground=primary_color,
            rowheight=24,
        )
        style.configure(
            "UVSim.Treeview.Heading",
            background=primary_color,
            foreground=secondary_color,
            relief="flat",
            borderwidth=0,
        )
        style.map(
            "UVSim.Treeview",
            background=[("selected", primary_color)],
            foreground=[("selected", secondary_color)],
        )

        style.configure(
            "UVSim.TNotebook",
            background=secondary_color,
            borderwidth=0,
        )
        style.configure(
            "UVSim.TNotebook.Tab",
            background=primary_color,
            foreground=secondary_color,
            padding=(10, 5),
        )
        style.map(
            "UVSim.TNotebook.Tab",
            background=[("selected", secondary_color), ("active", primary_color)],
            foreground=[("selected", primary_color), ("active", secondary_color)],
        )

    def apply_theme(self, primary_color, secondary_color):
        self._theme = (primary_color, secondary_color)
        self.root.configure(bg=primary_color)
        self.configure_styles(primary_color, secondary_color)
        self.root.update_idletasks()

        def apply_to_widget(widget):
            if isinstance(widget, tk.Button):
                widget.configure(
                    bg=secondary_color,
                    fg=primary_color,
                    activebackground=primary_color,
                    activeforeground=secondary_color,
                )
            elif isinstance(widget, tk.Label):
                widget.configure(bg=secondary_color, fg=primary_color)
            elif isinstance(widget, tk.Text):
                widget.configure(bg=secondary_color, fg=primary_color, insertbackground=primary_color)
            elif isinstance(widget, tk.Scrollbar):
                widget.configure(bg=secondary_color)
            elif isinstance(widget, tk.Frame):
                widget.configure(bg=secondary_color)
            elif isinstance(widget, ttk.Treeview):
                widget.configure(style="UVSim.Treeview")
            elif isinstance(widget, ttk.Notebook):
                widget.configure(style="UVSim.TNotebook")

            for child in widget.winfo_children():
                apply_to_widget(child)

        for widget in self.root.winfo_children():
            apply_to_widget(widget)
