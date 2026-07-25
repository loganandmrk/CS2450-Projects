import sys
from gui import UVSimGUI
import tkinter as tk
#create base structure for the main class.
def main():
    #Read file from command line and parse the input data and run a function to manipulate it

    root = tk.Tk()
    app = UVSimGUI(root)
    
    if len(sys.argv) == 2:
        app.load_file_from_path(sys.argv[1])
    elif len(sys.argv) > 2:
        print("Too many arguments presented. Launching GUI empty.")

    root.mainloop()

if __name__ == "__main__":
    main()
