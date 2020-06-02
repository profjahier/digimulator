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

with open('config.txt', 'r', encoding='utf-8') as f:
    config = f.readlines()
COLOR_DATA_LED = config[0].split(',')[0]
COLOR_ADDRESS_LED = config[1].split(',')[0]
COLOR_OFF = config[2].split(',')[0]
BGCOLOR = config[3].split(',')[0]
LINEWIDTH = 70

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
STACK_DEPTH = 4
OPSTACK_DEPTH = 256
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
    
def status_C(n, way='up'):
    """ toggles the Carry bit (bit 1) on the status register if necessary """
    if (n > 255 and way=='up') or (n < 0 and way=='down'):
        RAM[REG_STATUS] |= 2 # sets Carry bit to 1
        print_dbg('bit C status = 1')
        return True
    RAM[REG_STATUS] &= 253 # sets Carry bit to 0
    print_dbg('bit C status = 0')
    return False
            
def execute(mnemo):
    """ executes the instruction of mnemonic (mnemo is given in decimal base) """
    def halt():
        global run_mode
        run_mode = not(run_mode)
        can_run['bg'] = 'black'
        can_stop['bg'] = 'red'
    def stack_in(p):
        global SP
        if SP >= STACK_DEPTH:
        	halt() # stack overflow
        stack[SP] = PC
        SP += 1 # saves the address where to go after the next RETURN or RETURNLA
        
    def stack_out():
        global SP
        if SP < 0:
            halt() # stack underflow
        SP -= 1
        s = stack[SP]
        return s
    	
    global run_mode, PC, pause, accu, SP, OSP
    decoded_inst = ""
    if mnemo == 0:
        decoded_inst=("HALT")
        halt()
    elif mnemo == 1:
        decoded_inst=("NOP")
    elif mnemo == 2:
        decoded_inst=("SPEED " + str(RAM[PC+1]) )
        PC_next()
        pause = 1 + 2 * RAM[PC] 
        speed_rule.set(pause)
    elif mnemo == 3:
        decoded_inst=("COPYLR " + str(RAM[PC+1]) + " " + str(RAM[PC+2]) )
        PC_next()
        value = RAM[PC]
        PC_next()
        RAM[RAM[PC]] = value
    elif mnemo == 4:
        decoded_inst=("COPYLA " + str(RAM[PC+1]) )
        PC_next()
        accu = RAM[PC]
    elif mnemo == 5:
        decoded_inst=("COPYAR " + str(RAM[PC+1]) )
        PC_next()
        RAM[RAM[PC]] = accu
    elif mnemo == 6:
        decoded_inst=("COPYRA " + str(RAM[PC+1]) )
        PC_next()
        accu = RAM[RAM[PC]]
        status_Z(accu)
    elif mnemo == 7:
        decoded_inst=("COPYRR " + str(RAM[PC+1])+ " " + str(RAM[PC+2]) )
        PC_next()
        address = RAM[PC]
        PC_next()
        RAM[RAM[PC]] = RAM[address]
        status_Z(RAM[address])
    elif mnemo == 8:
        decoded_inst=("ADDLA " + str(RAM[PC+1]) )
        PC_next()
        value = RAM[PC]        
        if status_C(accu + value):
            accu += value - 256
        else:
            accu += value
        status_Z(accu)
    elif mnemo == 9:
        decoded_inst=("ADDRA " + str(RAM[PC+1]) )
        PC_next()
        value = RAM[RAM[PC]]
        if status_C(accu + value):
            accu += value - 256
        else:
            accu += value
        status_Z(accu)
    elif mnemo == 10:
        decoded_inst=("SUBLA " + str(RAM[PC+1]) )
        PC_next()
        value = RAM[PC]
        if status_C(accu - value, way='down'):
            accu += 256 - value
        else:
            accu -= value
        status_Z(accu)
    elif mnemo == 11:
        decoded_inst=("SUBRA " + str(RAM[PC+1]) )
        PC_next()
        value = RAM[RAM[PC]]
        if status_C(accu - value, way='down'):
            accu += 256 - value
        else:
            accu -= value
        status_Z(accu)
    elif mnemo == 12:
        decoded_inst=("ANDLA " + str(RAM[PC+1]) )
        PC_next()
        accu &= RAM[PC]
        status_Z(accu)
    elif mnemo == 13:
        decoded_inst=("ANDRA " + str(RAM[PC+1]) )
        PC_next()
        accu &= RAM[RAM[PC]]
        status_Z(accu)
    elif mnemo == 14:
        decoded_inst=("ORLA " + str(RAM[PC+1]) )
        PC_next()
        accu |= RAM[PC]
        status_Z(accu)
    elif mnemo == 15:
        decoded_inst=("ORRA " + str(RAM[PC+1]) )
        PC_next()
        accu |= RAM[RAM[PC]]
        status_Z(accu)
    elif mnemo == 16:
        decoded_inst=("XORLA " + str(RAM[PC+1]) )
        PC_next()
        accu ^= RAM[PC]
        status_Z(accu)
    elif mnemo == 17:
        decoded_inst=("XORRA " + str(RAM[PC+1]) )
        PC_next()
        accu ^= RAM[RAM[PC]]
        status_Z(accu)
    elif mnemo == 18:
        decoded_inst=("DECR " + str(RAM[PC+1]) )
        PC_next()
        address = RAM[PC]
        RAM[address]  = (-1 + RAM[address]) % 256
        status_Z(RAM[address])
    elif mnemo == 19:
        decoded_inst=("INCR " + str(RAM[PC+1]) )
        PC_next()
        address = RAM[PC]
        RAM[address]  = (1 + RAM[address]) % 256
        status_Z(RAM[address])
    elif mnemo == 20:
        decoded_inst=("DECRJZ " + str(RAM[PC+1]) )
        PC_next()
        address = RAM[PC]
        RAM[address] = (-1 + RAM[address]) % 256
        if status_Z(RAM[address]):
            PC += 2
    elif mnemo == 21:
        decoded_inst=("INCRJZ " + str(RAM[PC+1]) )
        PC_next()
        address = RAM[PC]
        RAM[address] = (1 + RAM[address]) % 256
        if status_Z(RAM[address]):
            PC += 2
    elif mnemo == 22:
        decoded_inst=("SHIFTRL " + str(RAM[PC+1]) )
        PC_next()
        address = RAM[PC]
        RAM[address] <<= 1 # shifts whitout taking care of the previous Carry bit
        carry = 1 if RAM[REG_STATUS] & 2 else 0 # gets the previous Carry bit on the status register
        RAM[address] += carry # sets the LSB equals to the previous Carry bit
        if status_C(RAM[address]):
            RAM[address] -= 256
    elif mnemo == 23:
        decoded_inst=("SHIFTRR " + str(RAM[PC+1]) )
        PC_next()
        address = RAM[PC]
        carry = 1 if RAM[REG_STATUS] & 2 else 0 # gets the previous Carry bit on the status register
        if RAM[address] % 2 == 1: # if odd value => raises a new Carry
            RAM[REG_STATUS] |= 2 # sets Carry bit to 1
        else:
            RAM[REG_STATUS] &= 253 # sets Carry bit to 0
        RAM[address] >>= 1 # shifts whitout taking care of the previous Carry bit
        RAM[address] += 128 * carry # sets the MSB equals to the previous Carry bit
    elif mnemo == 24:
        decoded_inst=("CBR " + str(RAM[PC+1]) + " " + str(RAM[PC+2]))
        PC_next()
        bit = RAM[PC]
        PC_next()
        RAM[RAM[PC]] &= (255-2**bit) # sets the specified bit to 0
    elif mnemo == 25:
        decoded_inst=("SBR " + str(RAM[PC+1]) + " " + str(RAM[PC+2]))
        PC_next()
        bit = RAM[PC]
        PC_next()
        RAM[RAM[PC]] |= 2**bit # sets the specified bit to 1
    elif mnemo == 26 or mnemo == 27:
        if mnemo == 26:
            decoded_inst=("BCRSC " + str(RAM[PC+1])+ " " + str(RAM[PC+2]) )
        else:
            decoded_inst=("BCRSS " + str(RAM[PC+1])+ " " + str(RAM[PC+2]) )
        PC_next()
        bit = RAM[PC]
        PC_next()
        if (mnemo == 26 and not(RAM[RAM[PC]] & 2**bit)) or (mnemo == 27 and (RAM[RAM[PC]] & 2**bit)):
            PC += 2
    elif mnemo == 28:
        decoded_inst=("JUMP " + str(RAM[PC+1]) )
        PC_next()
        PC = RAM[PC] - 1 # (-1) because of the "PC+1" after this actual execution
    elif mnemo == 29:
        decoded_inst=("CALL " + str(RAM[PC+1]) )
        PC_next()
        stack_in(PC)
        PC = RAM[PC] - 1 # (-1) because of the "PC+1 command" after this actual execution
    elif mnemo == 30:
        decoded_inst=("RETLA " + str(RAM[PC+1]) )
        PC_next()
        accu = RAM[PC]
        PC = stack_out() # to go back to the CALL
    elif mnemo == 31:
        decoded_inst=("RETURN" )
        PC = stack_out() # to go back to the CALL
    elif mnemo == 32:
        decoded_inst=("ADDRPC " + str(RAM[PC+1]) )
        PC_next()
        PC = (PC+RAM[RAM[PC]])%256
    elif mnemo == 33:
        decoded_inst=("INITSP" )
        SP = 0 # stack pointer
        OSP = 0
    elif mnemo == 34:
        decoded_inst=("RANDA" )
        accu = randint(0, 255)
    # Nouvelles instructions DGR2B
    elif mnemo == 35:
        decoded_inst=("COPYLI " + str(RAM[PC+1]) + " " + str(RAM[PC+2]) )
        PC_next()
        value = RAM[PC]
        PC_next()
        RAM[RAM[RAM[PC]]] = value
    elif mnemo == 36:
        decoded_inst=("COPYAI " + str(RAM[PC+1]) )
        PC_next()
        RAM[RAM[RAM[PC]]] = accu
    elif mnemo == 37:
        decoded_inst=("COPYIA " + str(RAM[PC+1]) )
        PC_next()
        accu = RAM[RAM[RAM[PC]]]
        status_Z(accu)
    elif mnemo == 38:
        decoded_inst=("COPYRI " + str(RAM[PC+1])+ " " + str(RAM[PC+2]) )
        PC_next()
        address = RAM[PC]
        PC_next()
        RAM[RAM[RAM[PC]]] = RAM[address]
        status_Z(RAM[address])
    elif mnemo == 39:
        decoded_inst=("COPYIR " + str(RAM[PC+1])+ " " + str(RAM[PC+2]) )
        PC_next()
        address = RAM[PC]
        PC_next()
        RAM[RAM[PC]] = RAM[RAM[address]]
        status_Z(RAM[RAM[address]])
    elif mnemo == 40:
        decoded_inst=("COPYII " + str(RAM[PC+1])+ " " + str(RAM[PC+2]) )
        PC_next()
        address = RAM[PC]
        PC_next()
        RAM[RAM[RAM[PC]]] = RAM[RAM[address]]
        status_Z(RAM[RAM[address]])
    elif mnemo == 41:
        decoded_inst=("SHIFTAL")
        accu <<= 1 # shifts whitout taking care of the previous Carry bit
        carry = 1 if RAM[REG_STATUS] & 2 else 0 # gets the previous Carry bit on the status register
        accu += carry # sets the LSB equals to the previous Carry bit
        if status_C(accu):
            accu -= 256
    elif mnemo == 42:
        decoded_inst=("SHIFTAR")
        carry = 1 if RAM[REG_STATUS] & 2 else 0 # gets the previous Carry bit on the status register
        if accu % 2 == 1: # if odd value => raises a new Carry
            RAM[REG_STATUS] |= 2 # sets Carry bit to 1
        else:
            RAM[REG_STATUS] &= 253 # sets Carry bit to 0
        accu >>= 1 # shifts whitout taking care of the previous Carry bit
        accu += 128 * carry # sets the MSB equals to the previous Carry bit
    elif mnemo == 43:
        decoded_inst=("JUMPI " + str(RAM[PC+1]) )
        PC_next()
        PC = RAM[RAM[PC]] - 1 # (-1) because of the "PC+1" after this actual execution
    elif mnemo == 44:
        decoded_inst=("CALLI " + str(RAM[PC+1]) )
        PC_next()
        stack_in(PC)
        PC = RAM[RAM[PC]] - 1 # (-1) because of the "PC+1 command" after this actual execution
    elif mnemo == 45:
        decoded_inst=("PUSH")
        if OSP >= OPSTACK_DEPTH:
        	halt() # stack overflow
        opstack[OSP] = accu
        OSP += 1 
    elif mnemo == 46:
        decoded_inst=("POP")
        if OSP == 0:
            halt() # stack underflow
        else:
            OSP -= 1
            accu = opstack[OSP]
            status_Z(accu)
    elif mnemo == 47:
        decoded_inst=("PUSHR" + str(RAM[PC+1]))
        if OSP >= OPSTACK_DEPTH:
        	halt() # stack overflow
        PC_next()
        address = RAM[PC]
        opstack[OSP] = RAM[address]
        OSP += 1 
    elif mnemo == 48:
        decoded_inst=("POPR" + str(RAM[PC+1]))
        PC_next()
        address = RAM[PC]
        if OSP == 0:
            halt() # stack underflow
        else:
            OSP -= 1
            RAM[address] = opstack[OSP]
            status_Z(RAM[address])
    elif mnemo == 49:
        decoded_inst=("PUSHI" + str(RAM[PC+1]))
        if OSP >= OPSTACK_DEPTH:
        	halt() # stack overflow
        PC_next()
        address = RAM[PC]
        opstack[OSP] = RAM[RAM[address]]
        OSP += 1 
    elif mnemo == 50:
        decoded_inst=("POPI" + str(RAM[PC+1]))
        PC_next()
        address = RAM[PC]
        if OSP == 0:
            halt() # stack underflow
        else:
            OSP -= 1
            RAM[RAM[address]] = opstack[OSP]
            status_Z(RAM[RAM[address]])
    elif mnemo == 51:
        decoded_inst=("HEAD")
        if OSP == 0:
            halt() # stack underflow
        else:
            accu = opstack[OSP-1]
            status_Z(accu)
    elif mnemo == 52:
        decoded_inst=("DEPTH")
        accu = OSP
        status_Z(accu)
    elif mnemo == 192:
        decoded_inst=("COMOUT")
        if accu == 10:
            #print()
            error_sv.set("")
        else:
            #print(chr(accu), end="")
            error_sv.set((error_sv.get()+chr(accu))[-LINEWIDTH-15:])
    elif mnemo == 193:
        decoded_inst=("COMIN")
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
    else: # digirule program stops if unknown mnemonic
        execute(0)
    if view_ram:
        sv_inst.set(decoded_inst)
    
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

def run():
    """ toggles run_mode, and starts running the program from the address defined by the address LEDs """
    global run_mode, PC, idle
    print_dbg(f'btn_run was pressed') 
    error_sv.set("")
    if run_mode and not(save_mode or load_mode):
        can_run['bg'] = 'black'
        can_stop['bg'] = 'red'
        run_mode = not(run_mode)
        switch_led(PC, frame='address')
        switch_led(RAM[PC], frame='data')
    elif not run_mode and not(save_mode or load_mode):
        can_run['bg'] = 'green'
        can_stop['bg'] = 'black'
        run_mode = not(run_mode)
        PC = b2d(read_from_led(frame='address')) # gets the address from where the program should start
        idle = True
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
    
def dbg_setpc(sender):
    """ goes to a specifc address (sets new PC) directly by double-clicking """
    global PC
    s = text_RAM.index(tk.CURRENT).split(".")
    if iv_hex.get()==1:
        l = int(s[0]) - 1
        c = (int(s[1]) - 5) // 3
    else:
        l = int(s[0]) - 1
        c = (int(s[1]) - 6) // 4
    PC = l * 8 + c
    display_ram()
    switch_led(PC, frame='address')
    switch_led(RAM[PC], frame='data')

def change_hexmode():
    if iv_hex.get()==1:
        text_RAM.configure(width=32)
    else: 
        text_RAM.configure(width=41)
    display_ram()

#
# editor functions
#

def assemble():
    global PC
    a = Assemble(edit_text.get("1.0", tk.END))
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
    for i in range(len(RAM)):
        RAM[i] = 0
    PC = 0
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
digirule.title("DIGIMULATOR : simulates a digirule 2A")
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
btn_run = ttk.Button(frame_run, text='Run/Stop ', command=run)
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
    engine.update_current_line(edit_text)

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
    engine.format_all(edit_text)
    update_line_numbers()  # After a paste we re-render the line numbers


engine.configure(edit_text)  # Configuration of the color engine (binds tags to colors)
engine.format_all(edit_text)  # Initial format
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
