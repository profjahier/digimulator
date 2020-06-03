import sys
import os.path
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {
    "copy_dependent_files": True,
    "packages": ["os", "tkinter", "serial"],
    "include_files": ["config.ini", "flash_memory.txt", "instructionset_2A.py", "instructionset_2B.py", "instructionset_2U.py"],
    "excludes": []
}

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(  name = "digimulator",
        version = "1.5",
        description = "Digirule2 assembler and simulator",
        author="Olivier Lecluse - Ronan Jahier - Thomas Lecluse",
        options = {"build_exe": build_exe_options},
        executables = [Executable("digimulator.py", base=base)])