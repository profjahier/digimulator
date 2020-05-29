#!/usr/bin/python3
# Ronan Jahier
# Olivier Lécluse
# Thomas Lécluse
# digirule 2A simulator 
# Licence GNU General Public License v3.0

import tkinter as tk
import tkinter.ttk as ttk
from assemble import Assemble
from cpu import Cpu
import color_engine as engine

def quit():
    digirule.quit()
    digirule.destroy()
#
# Interface
#


main_window = tk.Tk()
main_window.style = ttk.Style()
main_window.configure(background='#d9d9d9')
main_window.style.theme_use("alt")
main_window.title("DIGIMULATOR : simulates a digirule 2A")
ttk.Button(frame_edit, text='Quit', command=quit).pack()

reset()  # sets the environment when digirule starts
main_window.mainloop()
