import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {
    "packages": ["os", "tkinter", "serial"],
    "include_files": ["asm.py", "minidoc.pdf", "config.ini", "flash_memory.txt", "instructionset_2A.py", "instructionset_2B.py", "instructionset_2U.py"],
    "excludes": []
}

base = None
if sys.platform == "win32":
    base = "Win32GUI"
    if 'bdist_msi' in sys.argv:
        sys.argv += ['--initial-target-dir', 'c:\digimulator']

setup(  name = "digimulator",
        version = "1.6.1",
        description = "Digirule2 assembler and simulator",
        author="Olivier Lecluse - Ronan Jahier - Thomas Lecluse",
        options = {"build_exe": build_exe_options},
        executables = [Executable("digimulator.py", base=base)])
