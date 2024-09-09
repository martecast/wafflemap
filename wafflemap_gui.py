import tkinter as tk
from tkinter import ttk

from wafflemap import Wafflemap

# Create instance
win = tk.Tk()   

win.geometry("800x500")
win.title("Wafflemap GUI")
win.resizable(False, False)

def on_click():
    # buttons and labels can be modified as if they were global variables
    # by default ttk variables are module-level variables, that's why they can be accessed in q function
    pass

# Adding a Label
ttk.Label(win, text="A Label").grid(column=0, row=0) 
button = ttk.Button(win, text="button text", command=on_click)
button.grid(row=0, column=1)
#======================
# Start GUI
#======================
win.mainloop()