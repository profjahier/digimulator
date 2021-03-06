#!/usr/bin/python3
# Ronan Jahier
# Olivier Lécluse
# Thomas Lécluse
# digirule 2A simulator 
# Licence GNU General Public License v3.0

import tkinter as tk
import tkinter.ttk as ttk
from random import randint
from converter import b2d, d2b, d2h  # functions to convert from one base to another
from assemble import Assemble
import color_engine as engine
from indentator import indent
from line_numbers import LineNumberWidget
from dgrserial import ram2hex, comport, hex2ram
from tkinter import messagebox, simpledialog
import sys
import serial
from time import sleep
from configparser import ConfigParser
from importlib import import_module


# Read global configuration
VERSION = "version 1.6.1"
config = ConfigParser()
config.read('config.ini')
DR_model = config.get('main', 'DR_MODEL')
COLOR_DATA_LED = config.get('main', 'COLOR_DATA_LED')
COLOR_ADDRESS_LED = config.get('main', 'COLOR_ADDRESS_LED')
COLOR_OFF = config.get('main', 'COLOR_OFF')
BGCOLOR = config.get('main', 'BGCOLOR')
LINEWIDTH = 70

# Import the right instruction set according to the configuration file
instruction_set = import_module("instructionset_" + DR_model)

firmware_list = ["2A", "2B", "2U"]

# Global variables definitions
RAM = [0]*256 # empty 256 byte RAM
idle = True
pause = 1
accu = 0
load_mode, save_mode = False, False
flash_memory = []

REG_STATUS = 252
REG_BUTTON = 253
REG_ADDRESS = 254
REG_ADATA = 255

debug = False
run_mode = False
view_ram = True
import_flag = False
abort_flag = False
PC = 0
DIGIRULE_USB = ""

# Stack variables
# For digirule 2A stack is 4 bytes long
# For 2B, 2U and above, it is 16 bytes long
STACK_DEPTH = 4 if DR_model == "2A" else 16
OPSTACK_DEPTH = 64
stack = [0]*STACK_DEPTH
opstack = [0]*OPSTACK_DEPTH
SP = 0
OSP = 0

#
# Main code (digirule)
#

def print_dbg(*args,**kwargs):
    if debug:
        print(*args, **kwargs)

def PC_next():
    """ increments PC, waits for a while (pause according to speed) and displays LEDs """
    global PC, idle
    # On est libre pour traiter une instruction
    PC += 1
    # Bit 2 on status register = address LED function flag (logic 0 means the address LED’s function as normal – showing the currently accessed address
    # while a logic 1 means the address LED’s will show the data loaded into the addressLEDRegister)
    switch_led(RAM[REG_ADDRESS], frame='address') if RAM[REG_STATUS] & 4 else switch_led(PC, frame='address') 
    switch_led(RAM[REG_ADATA], frame='data')
    if idle:
        idle = False
        if pause == 1:
            can_address.after_idle(PC_next1) # pause in ms
        else:
            can_address.after(pause, PC_next1) # pause in ms
def PC_next1():
    """ Pause is over !!"""
    global idle
    idle = True

def status_Z(n):
    """ toggles the Zero bit (bit 0) on the status register if necessary """
    if n == 0:
         RAM[REG_STATUS] |= 1 # sets Zero bit to 1
         print_dbg('Z-bit status = 1')
         return True
    print_dbg('Z-bit status = 0')
    RAM[REG_STATUS] &= 254 # sets Zero bit to 0
    return False
    
def status_C(n):
    """ toggles the Carry bit (bit 1) on the status register if necessary """
    if (0 <= n <= 255):
        RAM[REG_STATUS] &= 253 # sets Carry bit to 0
        return n
    else:
        RAM[REG_STATUS] |= 2   # sets Carry bit to 1
        return n%256
            
def execute(mnemo):
    """ executes the instruction of mnemonic (mnemo is given in decimal base) """
    def halt():
        do_stop()
    def stack_in(p):
        global SP
        if SP >= STACK_DEPTH:
        	halt() # stack overflow
        else:
            stack[SP] = PC
            SP += 1 # saves the address where to go after the next RETURN or RETURNLA
        
    def stack_out():
        global SP
        if SP == 0:
            halt() # stack underflow
        else:
            SP -= 1
            s = stack[SP]
        return s
    def opcode(cmd):
        if cmd in inst_dic:
            return inst_dic[cmd]["code"]
        return -1

    global run_mode, PC, pause, accu, SP, OSP
    decoded_inst = ""
    inst_dic = instruction_set.inst_dic

    if mnemo == opcode("halt"):
        decoded_inst=("halt")
        halt()
    elif mnemo == opcode("nop"):
        decoded_inst=("nop")
    elif mnemo == opcode("speed"):
        decoded_inst=("speed " + str(RAM[PC+1]) )
        PC_next()
        pause = 1 + 2 * RAM[PC] 
        speed_rule.set(pause)
    elif mnemo == opcode("copylr"):
        decoded_inst=("copylr " + str(RAM[PC+1]) + " " + str(RAM[PC+2]) )
        PC_next()
        value = RAM[PC]
        PC_next()
        RAM[RAM[PC]] = value
        # Change of behaviour since 2A
        if DR_model != "2A":
            status_Z(value)
    elif mnemo == opcode("copyla"):
        decoded_inst=("copyla " + str(RAM[PC+1]) )
        PC_next()
        accu = RAM[PC]
        # Change of behaviour since 2A
        if DR_model != "2A":
            status_Z(accu)
    elif mnemo == opcode("copyar"):
        decoded_inst=("copyar " + str(RAM[PC+1]) )
        PC_next()
        RAM[RAM[PC]] = accu
        # Change of behaviour since 2A
        if DR_model != "2A":
            status_Z(accu)
    elif mnemo == opcode("copyra"):
        decoded_inst=("copyra " + str(RAM[PC+1]) )
        PC_next()
        accu = RAM[RAM[PC]]
        status_Z(accu)
    elif mnemo == opcode("copyrr"):
        decoded_inst=("copyrr " + str(RAM[PC+1])+ " " + str(RAM[PC+2]) )
        PC_next()
        address = RAM[PC]
        PC_next()
        RAM[RAM[PC]] = RAM[address]
        status_Z(RAM[address])
    elif mnemo == opcode("addla"):
        decoded_inst=("addla " + str(RAM[PC+1]) )
        carry = (RAM[REG_STATUS] & 2) // 2 # 0 or 1
        PC_next()
        value = RAM[PC]
        # Change of behaviour since 2A
        if DR_model != "2A":
            accu = status_C(accu + value + carry)
        else:
            accu = status_C(accu + value)
        status_Z(accu)
    elif mnemo == opcode("addra"):
        decoded_inst=("addra " + str(RAM[PC+1]) )
        carry = (RAM[REG_STATUS] & 2) // 2 # 0 or 1
        PC_next()
        value = RAM[RAM[PC]]
        if DR_model != "2A":
            accu = status_C(accu + value + carry)
        else:
            accu = status_C(accu + value)
        status_Z(accu)
    elif mnemo == opcode("subla"):
        # Carry = borrow
        decoded_inst=("subla " + str(RAM[PC+1]) )
        borrow = (RAM[REG_STATUS] & 2) // 2
        PC_next()
        value = RAM[PC]
        if DR_model != "2A":
            accu = status_C(accu - value - borrow)
        else:
            accu = status_C(accu - value)
        status_Z(accu)
    elif mnemo == opcode("subra"):
        decoded_inst=("subra " + str(RAM[PC+1]) )
        borrow = (RAM[REG_STATUS] & 2) // 2
        PC_next()
        value = RAM[RAM[PC]]
        if DR_model != "2A":
            accu = status_C(accu - value - borrow)
        else:
            accu = status_C(accu - value)
        status_Z(accu)
    elif mnemo == opcode("andla"):
        decoded_inst=("andla " + str(RAM[PC+1]) )
        PC_next()
        accu &= RAM[PC]
        status_Z(accu)
    elif mnemo == opcode("andra"):
        decoded_inst=("andra " + str(RAM[PC+1]) )
        PC_next()
        accu &= RAM[RAM[PC]]
        status_Z(accu)
    elif mnemo == opcode("orla"):
        decoded_inst=("orla " + str(RAM[PC+1]) )
        PC_next()
        accu |= RAM[PC]
        status_Z(accu)
    elif mnemo == opcode("orra"):
        decoded_inst=("orra " + str(RAM[PC+1]) )
        PC_next()
        accu |= RAM[RAM[PC]]
        status_Z(accu)
    elif mnemo == opcode("xorla"):
        decoded_inst=("xorla " + str(RAM[PC+1]) )
        PC_next()
        accu ^= RAM[PC]
        status_Z(accu)
    elif mnemo == opcode("xorra"):
        decoded_inst=("xorra " + str(RAM[PC+1]) )
        PC_next()
        accu ^= RAM[RAM[PC]]
        status_Z(accu)
    elif mnemo == opcode("decr"):
        decoded_inst=("decr " + str(RAM[PC+1]) )
        PC_next()
        address = RAM[PC]
        RAM[address]  = (-1 + RAM[address]) % 256
        status_Z(RAM[address])
    elif mnemo == opcode("incr"):
        decoded_inst=("incr " + str(RAM[PC+1]) )
        PC_next()
        address = RAM[PC]
        RAM[address]  = (1 + RAM[address]) % 256
        status_Z(RAM[address])
    elif mnemo == opcode("decrjz"):
        decoded_inst=("decrjz " + str(RAM[PC+1]) )
        PC_next()
        address = RAM[PC]
        RAM[address] = (-1 + RAM[address]) % 256
        if status_Z(RAM[address]):
            PC += 2
    elif mnemo == opcode("incrjz"):
        decoded_inst=("incrjz " + str(RAM[PC+1]) )
        PC_next()
        address = RAM[PC]
        RAM[address] = (1 + RAM[address]) % 256
        if status_Z(RAM[address]):
            PC += 2
    elif mnemo == opcode("shiftrl"):
        decoded_inst=("shiftrl " + str(RAM[PC+1]) )
        PC_next()
        address = RAM[PC]
        RAM[address] <<= 1                      # shifts whitout taking care of the previous Carry bit
        carry = (RAM[REG_STATUS] & 2) // 2      # 0 or 2 # gets the previous Carry bit on the status register
        RAM[address] += carry                   # sets the LSB equals to the previous Carry bit
        RAM[address] = status_C(RAM[address])
    elif mnemo == opcode("shiftrr"):
        decoded_inst=("shiftrr " + str(RAM[PC+1]) )
        PC_next()
        address = RAM[PC]
        carry = (RAM[REG_STATUS] & 2) // 2      # gets the previous Carry bit on the status register
        if RAM[address] % 2 == 1:               # if odd value => raises a new Carry
            status_C(256)                       # sets Carry bit to 1
        else:
            status_C(0)                         # sets Carry bit to 0
        RAM[address] >>= 1                      # shifts whitout taking care of the previous Carry bit
        RAM[address] += 128 * carry             # sets the MSB equals to the previous Carry bit
    elif mnemo == opcode("cbr"):
        decoded_inst=("cbr " + str(RAM[PC+1]) + " " + str(RAM[PC+2]))
        PC_next()
        bit = RAM[PC]
        PC_next()
        RAM[RAM[PC]] &= (255-2**bit) # sets the specified bit to 0
    elif mnemo == opcode("sbr"):
        decoded_inst=("sbr " + str(RAM[PC+1]) + " " + str(RAM[PC+2]))
        PC_next()
        bit = RAM[PC]
        PC_next()
        RAM[RAM[PC]] |= 2**bit # sets the specified bit to 1
    elif mnemo == opcode("tbr"):
        decoded_inst=("tbr " + str(RAM[PC+1]) + " " + str(RAM[PC+2]))
        PC_next()
        bit = RAM[PC]
        PC_next()
        RAM[RAM[PC]] ^= 2**bit # sets the specified bit to 1
    elif mnemo == opcode("bcrsc") or mnemo == opcode("bcrss"):
        if mnemo == opcode("bcrsc"):
            decoded_inst=("bcrsc " + str(RAM[PC+1])+ " " + str(RAM[PC+2]) )
        else:
            decoded_inst=("bcrss " + str(RAM[PC+1])+ " " + str(RAM[PC+2]) )
        PC_next()
        bit = RAM[PC]
        PC_next()
        if (mnemo == opcode("bcrsc") and not(RAM[RAM[PC]] & 2**bit)) or (mnemo == opcode("bcrss") and (RAM[RAM[PC]] & 2**bit)):
            PC += 2
    # bit instruction change from 2U
    elif mnemo == opcode("bclr"):
        decoded_inst=("bclr " + str(RAM[PC+1]) + " " + str(RAM[PC+2]))
        PC_next()
        bit = RAM[PC]
        PC_next()
        RAM[RAM[PC]] &= (255-2**bit) # sets the specified bit to 0
    elif mnemo == opcode("bset"):
        decoded_inst=("bset " + str(RAM[PC+1]) + " " + str(RAM[PC+2]))
        PC_next()
        bit = RAM[PC]
        PC_next()
        RAM[RAM[PC]] |= 2**bit # sets the specified bit to 1
    elif mnemo == opcode("bchg"):
        decoded_inst=("bchg " + str(RAM[PC+1]) + " " + str(RAM[PC+2]))
        PC_next()
        bit = RAM[PC]
        PC_next()
        RAM[RAM[PC]] ^= 2**bit # sets the specified bit to 1
    elif mnemo == opcode("btstsc") or mnemo == opcode("btstss"):
        if mnemo == opcode("bcrsc"):
            decoded_inst=("btstsc " + str(RAM[PC+1])+ " " + str(RAM[PC+2]) )
        else:
            decoded_inst=("btstss " + str(RAM[PC+1])+ " " + str(RAM[PC+2]) )
        PC_next()
        bit = RAM[PC]
        PC_next()
        if (mnemo == opcode("btstsc") and not(RAM[RAM[PC]] & 2**bit)) or (mnemo == opcode("btstss") and (RAM[RAM[PC]] & 2**bit)):
            PC += 2
    elif mnemo == opcode("jump"):
        decoded_inst=("jump " + str(RAM[PC+1]) )
        PC_next()
        PC = RAM[PC] - 1 # (-1) because of the "PC+1" after this actual execution
    elif mnemo == opcode("call"):
        decoded_inst=("call " + str(RAM[PC+1]) )
        PC_next()
        stack_in(PC)
        PC = RAM[PC] - 1 # (-1) because of the "PC+1 command" after this actual execution
    elif mnemo == opcode("retla"):
        decoded_inst=("retla " + str(RAM[PC+1]) )
        PC_next()
        accu = RAM[PC]
        PC = stack_out() # to go back to the CALL
    elif mnemo == opcode("return"):
        decoded_inst=("return" )
        PC = stack_out() # to go back to the CALL
    elif mnemo == opcode("addrpc"):
        decoded_inst=("addrpc " + str(RAM[PC+1]) )
        PC_next()
        PC = (PC+RAM[RAM[PC]])%256
    elif mnemo == opcode("initsp"):
        decoded_inst=("initsp" )
        SP = 0 # stack pointer
        OSP = 0
    elif mnemo == opcode("randa"):
        decoded_inst=("randa" )
        accu = randint(0, 255)
    # New instructions DGR2U
    elif mnemo == opcode("swapra"):
        decoded_inst=("swapra " + str(RAM[PC+1]) )
        PC_next()
        accu, RAM[RAM[PC]] = RAM[RAM[PC]], accu 
    elif mnemo == opcode("swaprr"):
        decoded_inst=("swaprr " + str(RAM[PC+1])+ " " + str(RAM[PC+2]) )
        PC_next()
        address = RAM[PC]
        PC_next()
        RAM[RAM[PC]], RAM[address] = RAM[address], RAM[RAM[PC]]
    elif mnemo == opcode("mul"):
        # MUL unsigned 8-bit multiply (3 bytes); 
        # on entry arg1 = multiplicand and arg2 = multiplier; 
        # on exit arg1 = product
        decoded_inst=("mul " + str(RAM[PC+1])+ " " + str(RAM[PC+2]) )
        PC_next()
        adr_arg1 = RAM[PC]
        PC_next()
        adr_arg2 = RAM[PC]
        RAM[adr_arg1] = status_C(RAM[adr_arg1] * RAM[adr_arg2])
        status_Z(RAM[adr_arg1])
    elif mnemo == opcode("div"):
        # DIV unsigned 8-bit divide (3 bytes); 
        # on entry arg1 = dividend and arg2 = divisor; 
        # on exit arg1 = quotient and accumulator = remainder
        decoded_inst=("div " + str(RAM[PC+1])+ " " + str(RAM[PC+2]) )
        PC_next()
        adr_arg1 = RAM[PC]
        PC_next()
        adr_arg2 = RAM[PC]
        dividend, divisor = RAM[adr_arg1], RAM[adr_arg2]
        if divisor == 0:
            # Exception : division by 0
            halt()
        else:
            RAM[adr_arg1] = dividend // divisor
            accu = dividend % divisor
            status_Z(RAM[adr_arg1])
            if accu == 0:
                # Remainder is 0, we activate the Carry flag
                status_C(256)
            else:
                status_C(0)
    # New instructions DGR2B
    elif mnemo == opcode("copyli"):
        decoded_inst=("copyli " + str(RAM[PC+1]) + " " + str(RAM[PC+2]) )
        PC_next()
        value = RAM[PC]
        PC_next()
        RAM[RAM[RAM[PC]]] = value
    elif mnemo == opcode("copyai"):
        decoded_inst=("copyai " + str(RAM[PC+1]) )
        PC_next()
        RAM[RAM[RAM[PC]]] = accu
    elif mnemo == opcode("copyia"):
        decoded_inst=("copyia " + str(RAM[PC+1]) )
        PC_next()
        accu = RAM[RAM[RAM[PC]]]
        status_Z(accu)
    elif mnemo == opcode("copyri"):
        decoded_inst=("copyri " + str(RAM[PC+1])+ " " + str(RAM[PC+2]) )
        PC_next()
        address = RAM[PC]
        PC_next()
        RAM[RAM[RAM[PC]]] = RAM[address]
        status_Z(RAM[address])
    elif mnemo == opcode("copyir"):
        decoded_inst=("copyir " + str(RAM[PC+1])+ " " + str(RAM[PC+2]) )
        PC_next()
        address = RAM[PC]
        PC_next()
        RAM[RAM[PC]] = RAM[RAM[address]]
        status_Z(RAM[RAM[address]])
    elif mnemo == opcode("copyii"):
        decoded_inst=("copyii " + str(RAM[PC+1])+ " " + str(RAM[PC+2]) )
        PC_next()
        address = RAM[PC]
        PC_next()
        RAM[RAM[RAM[PC]]] = RAM[RAM[address]]
        status_Z(RAM[RAM[address]])
    elif mnemo == opcode("shiftal"):
        decoded_inst=("shiftal")
        accu <<= 1 # shifts whitout taking care of the previous Carry bit
        carry = 1 if RAM[REG_STATUS] & 2 else 0 # gets the previous Carry bit on the status register
        accu += carry # sets the LSB equals to the previous Carry bit
        accu = status_C(accu)
    elif mnemo == opcode("shiftar"):
        decoded_inst=("shiftar")
        carry = 1 if RAM[REG_STATUS] & 2 else 0 # gets the previous Carry bit on the status register
        if accu % 2 == 1: # if odd value => raises a new Carry
            RAM[REG_STATUS] |= 2 # sets Carry bit to 1
        else:
            RAM[REG_STATUS] &= 253 # sets Carry bit to 0
        accu >>= 1 # shifts whitout taking care of the previous Carry bit
        accu += 128 * carry # sets the MSB equals to the previous Carry bit
    elif mnemo == opcode("jumpi"):
        decoded_inst=("jumpi " + str(RAM[PC+1]) )
        PC_next()
        PC = RAM[RAM[PC]] - 1 # (-1) because of the "PC+1" after this actual execution
    elif mnemo == opcode("calli"):
        decoded_inst=("calli " + str(RAM[PC+1]) )
        PC_next()
        stack_in(PC)
        PC = RAM[RAM[PC]] - 1 # (-1) because of the "PC+1 command" after this actual execution
    elif mnemo == opcode("sspush"):
        decoded_inst=("sspush")
        if OSP >= OPSTACK_DEPTH:
        	halt() # stack overflow
        opstack[OSP] = accu
        OSP += 1 
    elif mnemo == opcode("sspop"):
        decoded_inst=("sspop")
        if OSP == 0:
            halt() # stack underflow
        else:
            OSP -= 1
            accu = opstack[OSP]
            status_Z(accu)
    elif mnemo == opcode("sspushr"):
        decoded_inst=("sspushr" + str(RAM[PC+1]))
        if OSP >= OPSTACK_DEPTH:
        	halt() # stack overflow
        PC_next()
        address = RAM[PC]
        opstack[OSP] = RAM[address]
        OSP += 1 
    elif mnemo == opcode("sspopr"):
        decoded_inst=("sspopr" + str(RAM[PC+1]))
        PC_next()
        address = RAM[PC]
        if OSP == 0:
            halt() # stack underflow
        else:
            OSP -= 1
            RAM[address] = opstack[OSP]
            status_Z(RAM[address])
    elif mnemo == opcode("sspushi"):
        decoded_inst=("sspushi" + str(RAM[PC+1]))
        if OSP >= OPSTACK_DEPTH:
        	halt() # stack overflow
        PC_next()
        address = RAM[PC]
        opstack[OSP] = RAM[RAM[address]]
        OSP += 1 
    elif mnemo == opcode("sspopi"):
        decoded_inst=("sspopi" + str(RAM[PC+1]))
        PC_next()
        address = RAM[PC]
        if OSP == 0:
            halt() # stack underflow
        else:
            OSP -= 1
            RAM[RAM[address]] = opstack[OSP]
            status_Z(RAM[RAM[address]])
    elif mnemo == opcode("sshead"):
        decoded_inst=("sshead")
        if OSP == 0:
            halt() # stack underflow
        else:
            accu = opstack[OSP-1]
            status_Z(accu)
    elif mnemo == opcode("ssdepth"):
        decoded_inst=("ssdepth")
        accu = OSP
        status_Z(accu)
    elif mnemo == opcode("comout"):
        decoded_inst=("comout")
        if accu == 10:
            error_sv.set("")
        else:
            error_sv.set((error_sv.get()+chr(accu))[-LINEWIDTH-15:])
    elif mnemo == opcode("comin"):
        decoded_inst=("comin")
        try:
        	answer = (simpledialog.askstring("Simulation on Serial COMIN", "Input one Byte",
                                    parent=digirule))
        	if answer[0:2] == "0x":
        	    accu = int(answer,16)
        	elif answer[0:2] == "0b":
        	    accu = int(answer, 2)
        	else:
        	    accu = int(answer)
        except:
            accu = 0
    elif mnemo == opcode("comrdy"):
        decoded_inst=("comrdy")
        # if a caracter is available in the serial buffer
        # clears the zeroFlag
        # if no character awaits, sets the zeroflag
        answer = messagebox.askyesno("COMRDY","Is there anybody out there ?")
        status_Z(1) if answer else status_Z(0)
    else: # digirule program stops if unknown mnemonic
        execute(0)
    if view_ram:
        sv_inst.set(decoded_inst)
        # print (decoded_inst)
    
def program_run():
    """ runs the program ! """
    while run_mode: # 'fetch-decode-execute' cycle keeps running while no HALT mnemonic found
        if idle: # if not on pause
            mnemo = RAM[PC] # opcode
            display_ram()
            execute(mnemo)
            PC_next()
        can_address.update()
        can_data.update()
    switch_led(PC, frame='address') 
    switch_led(RAM[PC], frame='data')

def step():
    """ runs only one single step of the program """
    mnemo = RAM[PC] # opcode
    display_ram()
    execute(mnemo)
    PC_next()

def do_stop():
    global run_mode, idle
    can_run['bg'] = 'black'
    can_stop['bg'] = 'red'
    run_mode = False
    switch_led(PC, frame='address')
    switch_led(RAM[PC], frame='data')
    btn_run.state(['!pressed'])
    btn_run.configure(text='Run')
def do_run():
    global run_mode, idle
    can_run['bg'] = 'green'
    can_stop['bg'] = 'black'
    run_mode = True
    idle = True
    btn_run.state(['pressed'])
    btn_run.configure(text='Stop')
    error_sv.set("")

def run():
    """ toggles run_mode, and starts running the program from the address defined by the address LEDs """
    global PC
    print_dbg(f'btn_run was pressed') 
    if run_mode and not(save_mode or load_mode):
        do_stop()
        switch_led(PC, frame='address')
        switch_led(RAM[PC], frame='data')
    elif not run_mode and not(save_mode or load_mode):
        do_run()
        PC = b2d(read_from_led(frame='address')) # gets the address from where the program should start
        program_run() # run : let's go !
        
def prev():
    """ PC = PC - 1, and displays new address and data stored at this actual address """
    global PC
    if not (run_mode or save_mode or load_mode):
        print_dbg('action prev')
        sv_inst.set("")
        PC = 255 if PC == 0 else PC - 1
        switch_led(PC, frame='address')
        switch_led(RAM[PC], frame='data')
        display_ram()
    
def next_():
    """ PC = PC + 1, and displays new address and data stored at this actual address """
    global PC
    if not (run_mode or save_mode or load_mode):
        print_dbg('action next')
        sv_inst.set("")
        PC = 0 if PC == 255 else PC + 1
        switch_led(PC, frame='address')
        switch_led(RAM[PC], frame='data')
        display_ram()
    
def goto():
    """ sets PC to the address defined by the address LEDS,
    and displays new address and data stored at this actual address """
    global PC
    if not (run_mode or save_mode or load_mode):
        print_dbg('action goto')
        sv_inst.set("")
        leds = read_from_led('data')
        PC = b2d(leds)
        switch_led(PC, frame='address')
        switch_led(RAM[PC], frame='data')
        display_ram()
    
def store():
    """ stores the data defined by the data LEDS at the address defined by the address LEDS,
    and goes to next address (PC = PC + 1) """
  #  global RAM
    if not (run_mode or save_mode or load_mode):
        print_dbg('action store')
        RAM[PC] = b2d(read_from_led('data'))
        print_dbg(RAM)
        next_()
        display_ram()
    
def load():
    """ sets the load_mode to load a program to the RAM from the flash memory """
    global RAM, PC, load_mode
    if not (run_mode or save_mode):
        print_dbg('action load')
        if not (run_mode or save_mode):
            load_mode = True
            btn_load.state(['pressed'])
    
def save():
    """ sets the save_mode to save RAM to a program on the flash memory """
    global flash_memory, save_mode
    if not (run_mode or load_mode):
        print_dbg('action save')
        if not (run_mode or load_mode):
            save_mode = True
            btn_save.state(['pressed'])
    
def switch_led(n, frame='data', mode='int'):
    """ displays a number 'n' on the LEDs.
    mode = 'str' : the number is given as an "8-bit" string
    mode = 'int' : the number is given as an integer (decimal base) """
    can = can_data if frame == 'data' else can_address
    color = COLOR_DATA_LED if frame == 'data' else COLOR_ADDRESS_LED
    leds = n if mode == 'str' else d2b(n)
    for i,bit in enumerate(leds):
        if bit == '1':
            can.itemconfig('L'+str(7-i), fill=color, outline=color)
        else:
            can.itemconfig('L'+str(7-i), fill=COLOR_OFF, outline=COLOR_OFF)
        
def read_from_led(frame='data'):
    """ gets the LEDs state as an '8-bit' string """
    can = can_data if frame == 'data' else can_address
    color_ref = COLOR_DATA_LED if frame == 'data' else COLOR_ADDRESS_LED
    bits = ''
    for i in range(8):
        COLOR = can.itemcget('L'+str(7-i), 'fill')
        if COLOR == color_ref:
            bits += '1'
        else:
            bits += '0'
    return bits
    
def led_toggle(i, frame='data'):
    """ toggles i-LED state (on or off) """
    can = can_data if frame == 'data' else can_address
    color_ref = COLOR_DATA_LED if frame == 'data' else COLOR_ADDRESS_LED
    COLOR = can.itemcget('L'+str(i), 'outline')
    COLOR = color_ref if COLOR == COLOR_OFF else COLOR_OFF
    can.itemconfig('L'+str(i), fill=COLOR, outline=COLOR)
    
def btn_i(i):
    """ manages the consequence of pressing the buttons (according to the actual mode : run, load or save) """
    global PC, load_mode, save_mode, flash_memory
    print_dbg('press on btn'+str(i))

    if load_mode:   # loads a program (n°i) to the RAM from the flash memory """
        with open('flash_memory.txt', 'r', encoding='utf-8') as f:
            flash_memory = f.readlines() 
        start = 256*i # where the program n°i starts in the flash memory
        for j in range(start, start+256):
            RAM[j-start] = int(flash_memory[j][:-1])
        print_dbg(RAM)         
        PC = 0
        RAM[REG_BUTTON] = 0
        load_mode = not load_mode
        btn_load.state(['!pressed'])
        switch_led(PC, frame='address')
        switch_led(RAM[PC], frame='data')
        
    elif save_mode: # saves RAM to a program n°i on the flash memory
        start = 256*i # where the program n°i starts in the flash memory
        with open('flash_memory.txt', 'w', encoding='utf-8') as f:
            for j in range(0, start):
                f.write(flash_memory[j])
            for j in range(start, start + 256):
                f.write(str(RAM[j-start])+'\n')
            for j in range(start + 256, len(flash_memory)):
                f.write(flash_memory[j])
        save_mode = not save_mode
        btn_save.state(['!pressed'])
    
    elif run_mode: 
        pass
    
    else:
        led_toggle(i, 'data')
        RAM[REG_BUTTON] ^= 2**i
    display_ram()

def btn_i_pressed(i):
    """ manages the consequence of pressing a button in run_mode """
    if run_mode: 
        RAM[REG_BUTTON] |= 2**i
        display_ram()
        print_dbg("press ", i)

def btn_i_released(i):
    """ manages the consequence of releasing a button in run_mode """
    if run_mode: 
        RAM[REG_BUTTON] &= 255-2**i
        display_ram()
        print_dbg("release ", i)

def reset():
    """ sets the environment when digirule starts """
    global SP,PC, run_mode, flash_memory, pause, accu, load_mode, save_mode, idle
    pause = 1 # pause (in ms) between 2 executions on run_mode
    PC = 0 # Program Counter => address of RAM
    SP = 0 # Stack Pointer
    OSP = 0
    switch_led(PC, frame='address')
    run_mode, load_mode, save_mode = False, False, False
    switch_led(RAM[PC], frame='data')
    accu = 0 # accumulator register
    idle = True
    display_ram()
    with open('flash_memory.txt', 'r', encoding='utf-8') as f:
        flash_memory = f.readlines()

def change_speed(sender):
    """ sets the speed while programm running (not implemented on actual digirule) """
    global pause
    pause = int(speed_rule.get())
    
#
# debugger
#

def show_ram():
    """ toggles RAM display """
    global view_ram
    view_ram = not view_ram
    if view_ram:
        btn_dbg.configure(text='Hide RAM')
        btn_dbg.state(['pressed'])
        display_ram()
    else:
        btn_dbg.configure(text='Show RAM')
        btn_dbg.state(['!pressed'])
        text_RAM.config(state=tk.NORMAL)
        text_RAM.delete("1.0",tk.END)
        sv_acc.set("")
        sv_pc.set("")
        sv_sp.set("")
        sv_status.set("")
        sv_inst.set("")

def display_ram():
    """ 256 byte RAM displayed on the right side of the digirule.
    32 lines of 8 bytes """
    if view_ram:
        text_RAM.config(state=tk.NORMAL)
        text_RAM.delete("1.0",tk.END)

        for l in range(32):
            line = d2h(l*8, iv_hex.get())+":  "
            for c in range(8):
                line += d2h(RAM[l*8+c], iv_hex.get())+" "
            if l != 31:
                line +="\n"
            text_RAM.insert(tk.END, line)
        
        lpc = PC // 8 + 1
        if iv_hex.get()==1:
            cpc = PC % 8 * 3 + 5
            clen=2
        else:
            cpc = PC % 8 * 4 + 6
            clen=3
        text_RAM.mark_set("debut", "%d.%d"%(lpc,cpc))
        text_RAM.mark_set("fin", "%d.%d"%(lpc,cpc+clen))
        text_RAM.tag_add("pc", "debut", "fin")
        text_RAM.config(state=tk.DISABLED)

        sv_acc.set(f"AC = {d2b(accu)} (dec : {str(accu)})")
        hexmode_str = "hex" if iv_hex.get() == 1 else "dec"
        sv_pc.set(f"PC  =  {d2b(PC)} ({hexmode_str} : {d2h(PC, iv_hex.get())})")
        stack_str = "stack : "
        for i in range(SP):
            stack_str += d2h(stack[i], iv_hex.get()) + " "
        sv_sp.set(stack_str)
        sv_status.set(f"ST  = {d2b(RAM[REG_STATUS])}")

def dbg_setpc_cs():
    text_RAM.tag_remove(tk.SEL, "0.0", tk.END)

def dbg_setpc(sender):
    """ goes to a specifc address (sets new PC) directly by double-clicking """
    global PC, run_mode, idle
    # First we stop the execution
    do_stop()
    s = text_RAM.index(tk.CURRENT).split(".")
    if iv_hex.get()==1:
        l = int(s[0]) - 1
        c = (int(s[1]) - 5) // 3
    else:
        l = int(s[0]) - 1
        c = (int(s[1]) - 6) // 4
    PC = l * 8 + c
    if not (0 <= PC <= 255):
        PC=0
    display_ram()
    switch_led(PC, frame='address')
    switch_led(RAM[PC], frame='data')
    text_RAM.after(1,dbg_setpc_cs)

def change_hexmode():
    if iv_hex.get()==1:
        text_RAM.configure(width=32)
    else: 
        text_RAM.configure(width=41)
    display_ram()

#
# editor functions
#
def change_fw(event):
    global instruction_set, STACK_DEPTH, DR_model, stack, SP
    DR_model = fw_combo.get()
    config.set('main', 'DR_MODEL', DR_model)

    # load instruction set
    instruction_set = import_module("instructionset_" + DR_model)
    
    # change stack size according to firmware
    STACK_DEPTH = 4 if DR_model == "2A" else 16
    stack = [0] * STACK_DEPTH
    SP = 0

    # refresh color syntax highlighting
    engine.format_all(edit_text, instruction_set.inst_dic)
    with open('config.ini', 'w') as f:
        config.write(f)

def assemble():
    global PC
    a = Assemble(edit_text.get("1.0", tk.END), instruction_set.inst_dic)
    res = a.parse()
    if res[0]:
        # No error during assembly process
        assembled_ram = res[1]
        # print(assembled_ram)
        error_sv.set("Success ! program occupation :"+str(len(assembled_ram))+"/255")
        # copy assembled program in RAM
        for i in range(len(assembled_ram)):
            RAM[i] = assembled_ram[i]
        PC = 0
        display_ram()
        switch_led(PC, frame='address')
        switch_led(RAM[PC], frame='data')
    else:
        error_sv.set(res[1])
        error_line = res[2]
        if error_line != 0:
            edit_text.mark_set("err_line_begin", "%d.0" % error_line)
            edit_text.mark_set("err_line_end", "%d.end" % error_line)
            edit_text.tag_add("error", "err_line_begin", "err_line_end")
            edit_text.tag_config("error", background="red")
        else:
            index = edit_text.search(res[3], "1.0", nocase=1)
            l, c = index.split(".")
            c = str(int(c)+len(res[3]))
            edit_text.mark_set("err_line_begin", index)
            edit_text.mark_set("err_line_end", l+"."+c)
            edit_text.tag_add("error", "err_line_begin", "err_line_end")
            edit_text.tag_config("error", background="orange")


def clearmem():
    global PC, SP, OSP
    for i in range(len(RAM)):
        RAM[i] = 0
    PC = 0
    SP = 0 # stack pointer
    OSP = 0
    display_ram()
    switch_led(PC, frame='address')
    switch_led(RAM[PC], frame='data')


def remove_err(sender):
    #removes the error tag
    edit_text.tag_delete("error")


def quit():
    digirule.quit()
    digirule.destroy()

#
# Serial communication
#
def export():
    global DIGIRULE_USB

    dump = ram2hex(RAM)
    dgr_serial = comport(2400, digirule, port = DIGIRULE_USB)
    if dgr_serial:
        DIGIRULE_USB = dgr_serial.port
        error_sv.set("Dumpimg memory on port " + DIGIRULE_USB)
        error_lbl.update()
        # print (DIGIRULE_USB)
        try:
            dgr_serial.open()
        except serial.serialutil.SerialException as ex:
            error_sv.set(ex)
        else:
            for line in dump.splitlines():
                dgr_serial.write(line.encode("utf-8"))
                sleep(0.1)
            sleep(2)
            dgr_serial.close()
            error_sv.set("Memory sent")
            answer = messagebox.askyesno("Question","Is the transfert OK ??")
            if not answer:
                DIGIRULE_USB = ""
            error_sv.set("")
    else:
        # print("No USB UART interface detected")
        DIGIRULE_USB = ""

def importram():
    global DIGIRULE_USB, import_flag, abort_flag

    if import_flag:
        abort_flag = True
        btn_import.state(['!pressed'])
        return

    import_flag = True
    btn_import.state(['pressed'])

    dgr_serial = comport(2400, digirule, port = DIGIRULE_USB)
    if dgr_serial:
        DIGIRULE_USB = dgr_serial.port
        error_sv.set("Receiving RAM from Digirule on port " + DIGIRULE_USB)
        error_lbl.update()
        try:
            dgr_serial.open()
        except serial.serialutil.SerialException as ex:
            error_sv.set(ex)
        else:
            # Waiting for the digirule to transmit
            # with ability to abort
            while (dgr_serial.in_waiting == 0) and not abort_flag:
                btn_import.update()
            import_flag = False
            if abort_flag:
                abort_flag = False
                error_sv.set("Abort transfert")
                dgr_serial.close()
                return
            else:
                # Digirule is transmitting
                error_sv.set("Digirule is transmitting")
                error_lbl.update()
                listdump = dgr_serial.readlines()
                dgr_serial.close()
                btn_import.state(['!pressed'])
                hexdump = ""
                for line in listdump:
                    hexdump += line.decode('utf-8')
                # print (hexdump)
                try:
                    newram = hex2ram(hexdump)
                except ValueError:
                    error_sv.set("Checksum error")
                else:
                    # Ram is received and no checksum error
                    # writing newram in RAM
                    error_sv.set("Memory received")
                    for i,r in enumerate(newram):
                        RAM[i] = r
                    display_ram()
                    text_RAM.update()
                    answer = messagebox.askyesno("Question","Is the transfert OK ??")
                    if not answer:
                        DIGIRULE_USB = ""
                    error_sv.set("")
    else:
        # print("No USB UART interface detected")
        DIGIRULE_USB = ""
    import_flag = False

#
# Interface
#


digirule = tk.Tk()
digirule.style = ttk.Style()
digirule.style.configure('TFrame', background='green')
digirule.config(bg=BGCOLOR)
digirule.style.theme_use("alt")
digirule.title("DIGIMULATOR : simulates a digirule 2x - " + VERSION)
digirule.resizable(0, 0)

frame_left = ttk.Frame(digirule, style='TFrame')
frame_left.pack(side=tk.LEFT)
frame_dr = ttk.Frame(frame_left)
frame_dr.pack(side=tk.TOP)
frame_edit = ttk.Frame(frame_left)
frame_edit.pack()
frame_dbg = ttk.Frame (digirule)
frame_dbg.pack(side=tk.LEFT)

frame_reg = ttk.Frame(frame_dbg)
frame_reg.pack(side=tk.TOP)
frame_ram = ttk.Frame(frame_dbg)
frame_ram.pack()

# Interface digirule
frame_run = ttk.Frame(frame_dr)
frame_run.pack()
btn_run = ttk.Button(frame_run, text='Run', command=run)
btn_run.pack(side=tk.LEFT)
btn_step = ttk.Button(frame_run, text='Step ', command=step)
btn_step.pack(side=tk.LEFT)
frame_state = ttk.Frame(frame_run)
frame_state.pack(side=tk.LEFT)
can_run = tk.Canvas(frame_state, width=30, height=10, bg='black')
can_run.pack(side=tk.TOP)
can_stop = tk.Canvas(frame_state, width=30, height=10, bg='red')
can_stop.pack(side=tk.BOTTOM)
btn_dbg = ttk.Button(frame_run, text='Hide RAM', command=show_ram)
btn_dbg.state(['pressed'])
btn_dbg.pack(side=tk.LEFT)
ttk.Label(frame_run, text = " Digirule").pack(side=tk.LEFT, padx=5)
fw_combo = ttk.Combobox(frame_run, values=firmware_list, width=3)
fw_combo.current(firmware_list.index(DR_model))
fw_combo.bind("<<ComboboxSelected>>", change_fw)
fw_combo.pack(side=tk.LEFT)
frame_goto = ttk.Frame(frame_dr)
frame_goto.pack()
ttk.Button(frame_goto, text='Goto', command=goto).pack(side=tk.LEFT)
ttk.Button(frame_goto, text='Prev.', command=prev).pack(side=tk.LEFT)
ttk.Button(frame_goto, text='Next', command=next_).pack(side=tk.LEFT)
ttk.Button(frame_goto, text='Store', command=store).pack(side=tk.LEFT)
frame_file = ttk.Frame(frame_dr)
frame_file.pack()
btn_import = ttk.Button(frame_file, text='from Digirule', command=importram)
btn_import.pack(side=tk.LEFT)
btn_load = ttk.Button(frame_file, text='Load', command=load)
btn_load.pack(side=tk.LEFT)
btn_save = ttk.Button(frame_file, text='Save', command=save)
btn_save.pack(side=tk.LEFT)
btn_export = ttk.Button(frame_file, text='to Digirule', command=export)
btn_export.pack(side=tk.LEFT)
speed_rule = ttk.Scale(frame_dr, from_=0, to=1000, orient=tk.HORIZONTAL, length=300, command=change_speed)
speed_rule.pack()
frame_address = ttk.Frame(frame_dr)
frame_address.pack()
can_address = tk.Canvas(frame_dr, width=340, height=40, background='white')
can_address.pack()
for i in range(8):
    can_address.create_oval((20*(2*i+1)), 10, (20*(2*i+2)), 30, outline=COLOR_ADDRESS_LED, fill=COLOR_ADDRESS_LED, tags='L'+str(7-i))

frame_data = ttk.Frame(frame_dr)
frame_data.pack()
can_data = tk.Canvas(frame_dr, width=340, height=40, background='white')
can_data.pack()
for i in range(8):
    can_data.create_oval((20*(2*i+1)), 10, (20*(2*i+2)), 30, outline=COLOR_DATA_LED, fill=COLOR_DATA_LED, tags='L'+str(7-i))

frame_btn = ttk.Frame(frame_dr, width=340)
frame_btn.pack()
for i in range(7, -1, -1):
    btn = ttk.Button(frame_btn, text=str(i), width=4, command=lambda i=i:btn_i(i))
    btn.pack(side=tk.LEFT)
    btn.bind("<ButtonPress>", lambda sender, i=i:btn_i_pressed(i))
    btn.bind("<ButtonRelease>", lambda sender, i=i:btn_i_released(i))

# editor GUI
error_sv = tk.StringVar()
frame_txt = ttk.Frame(frame_edit, width=630, height=500)
frame_txt.pack(fill="both", expand=True)
frame_txt.grid_propagate(True)
frame_txt.grid_rowconfigure(0, weight=1)
frame_txt.grid_columnconfigure(0, weight=1)
# Editor
edit_text = tk.Text(frame_txt, width=LINEWIDTH, height=25, background='black', fg='green', insertbackground='yellow', wrap=tk.NONE)
edit_text.grid(row=0, column=1, sticky="nsew", padx=2, pady=2)
# Line numbers
linenumbers = LineNumberWidget(edit_text, frame_txt, width=3, state="disable")
linenumbers.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)


# Scroll bar
def on_scrollbar(*args):
    """
    Scrolls both the editor and the line numbers text widgets
    """
    edit_text.yview(*args)
    linenumbers.yview(*args)


def on_textscroll(*args):
    """
    Moves the scrollbar and scrolls the editor and the line numbers text widgets
    """
    scrollb.set(*args)
    on_scrollbar('moveto', args[0])
    linenumbers.prev_posi = args[0]  # Save this position in case we perform a re_render on the line numbers


scrollb = ttk.Scrollbar(frame_txt, command=on_scrollbar)
edit_text['yscrollcommand'] = on_textscroll
scrollb.grid(row=0, column=2, sticky='nsew')


def update_line_numbers():
    """
    Calls a re-render on the line numbers widget and scrolls back to the current posiiton
    """
    linenumbers.re_render()
    if linenumbers.prev_posi:
        on_scrollbar('moveto', linenumbers.prev_posi)  # Scroll back to previous position


edit_text.insert("1.0", "// See examples from https://github.com/profjahier/digimulator/\n// to learn more about the syntax and keywords")
assemble_btn = ttk.Button(frame_edit, text="Assemble", command=assemble)
assemble_btn.pack()
error_lbl = ttk.Label(frame_edit, textvariable=error_sv, anchor = tk.W, borderwidth = 1, width=-50, wraplength=600, padding=5,
                relief=tk.SUNKEN, background = "black", foreground = "green")
error_lbl.pack()


# Color Engine
def on_key_pressed(event):
    """
    Callback method for the color update event. Calls for an update on the cursors' position line
    """
    remove_err(event)
    engine.update_current_line(edit_text, instruction_set.inst_dic)

    if event.keysym == "Return":  # Indent process
        indent(edit_text)

    if event.keysym in ("Return", "Delete", "BackSpace"):
        update_line_numbers()


def on_paste(event):
    """
    Callback method for <<Paste>> event. This will trigger a complete update of the code's coloration
    """
    edit_text.after(30, recolor_after)


def recolor_after():
    """
    Callback method. This calls the format_all method of the color engine
    """
    engine.format_all(edit_text, instruction_set.inst_dic)
    update_line_numbers()  # After a paste we re-render the line numbers


engine.configure(edit_text)  # Configuration of the color engine (binds tags to colors)
engine.format_all(edit_text, instruction_set.inst_dic)  # Initial format
update_line_numbers()  # First line update

edit_text.bind("<KeyRelease>", on_key_pressed)
edit_text.bind("<<Paste>>", on_paste)


# debugger GUI

sv_acc = tk.StringVar()
sv_status = tk.StringVar()
sv_pc = tk.StringVar()
sv_sp = tk.StringVar()
sv_inst = tk.StringVar()
iv_hex = tk.IntVar()
iv_hex.set(1)

label_sp = ttk.Label(frame_reg, textvariable=sv_sp, anchor = tk.W,width=25)
label_sp.pack()
label_pc = ttk.Label(frame_reg, textvariable=sv_pc, anchor = tk.W,width=25)
label_pc.pack()
label_inst = ttk.Label(frame_reg, textvariable=sv_inst, background="black", 
            foreground="green", border=1, relief = tk.SUNKEN, anchor = tk.W,width=15)
label_inst.pack()

label_acc = ttk.Label(frame_reg, textvariable=sv_acc, anchor = tk.W,width=25)
label_acc.pack()

label_status = ttk.Label(frame_reg, textvariable=sv_status, anchor = tk.W,width=25)
label_status.pack()

text_RAM = tk.Text(frame_dbg, width=32, height=32, bg='black', fg='green')
text_RAM.tag_config("pc", background="yellow")
text_RAM.bind("<Double-Button-1>", dbg_setpc)
text_RAM.pack(pady=10)

hex_cb = ttk.Checkbutton(frame_dbg, variable=iv_hex, text="Hexadecimal mode", onvalue=1, offvalue=0, command=change_hexmode)
hex_cb.pack()

clearmem_btn = ttk.Button(frame_dbg, text="! Clear Memory !", command=clearmem)
clearmem_btn.pack(pady=10)

ttk.Button(frame_edit, text='Quit', command=quit).pack()

reset()  # sets the environment when digirule starts
digirule.mainloop()
print("Goodbye!")
