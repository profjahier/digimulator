#!/usr/bin/python3
# Ronan Jahier
# Olivier Lécluse
# Thomas Lécluse
# digirule 2A simulator 
# Licence GNU General Public License v3.0

class Cpu:
    def __init__(self):
        self.RAM = [0]*256 # empty 256 byte RAM
        self.accu = 0
        self.run_mode = False
        self.PC = 0
        # Stack variables
        self.STACK_DEPTH = 4
        self.OPSTACK_DEPTH = 256
        self.stack = [0]*STACK_DEPTH
        self.opstack = [0]*OPSTACK_DEPTH
        self.SP = 0
        self.OSP = 0
    
    def b2d(b):
        """ convertit une chaine de 8 bits en nb décimal 
        entrée : b = chaine de 8 caractères ('0' ou '1') 
        sortie : d = nb entier (base décimale) """
        d = 0
        for i,n in enumerate(b):
            d += 2**(7-i) * int(n)
        return d
        
    def d2b(d):
        """ convertit un entier en une chaine de 8 bits 
        entrée : d = nb entier (base décimale)
        sortie : chaine de 8 caractères ('0' ou '1')  """
        return bin(d)[2:].rjust(8, '0')


    def d2h(d, mode):
        """ convertit un entier en une chaine de 2 caractères hexadécimaux 
        entrée : d = nb entier (base décimale)
        sortie : chaine de 2 caractères ('0' à 'F')  """
        if mode==1:
            return hex(d)[2:].rjust(2, '0')
        else:
            return str(d).rjust(3, '0')
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
            stack[SP] = PC
            SP += 1 # saves the address where to go after the next RETURN or RETURNLA
            if SP >= STACK_DEPTH:
                halt() # stack overflow
        def stack_out():
            global SP
            SP -= 1
            s = stack[SP]
            if SP < 0:
                halt() # stack underflow
            return s
            
        global run_mode, PC, pause, accu, SP, OSP
        if mnemo == 0:
            sv_inst.set("HALT")
            halt()
        elif mnemo == 1:
            sv_inst.set("NOP")
        elif mnemo == 2:
            sv_inst.set("SPEED " + str(RAM[PC+1]) )
            PC_next()
            pause = 1 + 2 * RAM[PC] 
            speed_rule.set(pause)
        elif mnemo == 3:
            sv_inst.set("COPYLR " + str(RAM[PC+1]) + " " + str(RAM[PC+2]) )
            PC_next()
            value = RAM[PC]
            PC_next()
            RAM[RAM[PC]] = value
        elif mnemo == 4:
            sv_inst.set("COPYLA " + str(RAM[PC+1]) )
            PC_next()
            accu = RAM[PC]
        elif mnemo == 5:
            sv_inst.set("COPYAR " + str(RAM[PC+1]) )
            PC_next()
            RAM[RAM[PC]] = accu
        elif mnemo == 6:
            sv_inst.set("COPYRA " + str(RAM[PC+1]) )
            PC_next()
            accu = RAM[RAM[PC]]
            status_Z(accu)
        elif mnemo == 7:
            sv_inst.set("COPYRR " + str(RAM[PC+1])+ " " + str(RAM[PC+2]) )
            PC_next()
            address = RAM[PC]
            PC_next()
            RAM[RAM[PC]] = RAM[address]
            status_Z(RAM[address])
        elif mnemo == 8:
            sv_inst.set("ADDLA " + str(RAM[PC+1]) )
            PC_next()
            value = RAM[PC]        
            if status_C(accu + value):
                accu += value - 256
            else:
                accu += value
            status_Z(accu)
        elif mnemo == 9:
            sv_inst.set("ADDRA " + str(RAM[PC+1]) )
            PC_next()
            value = RAM[RAM[PC]]
            if status_C(accu + value):
                accu += value - 256
            else:
                accu += value
            status_Z(accu)
        elif mnemo == 10:
            sv_inst.set("SUBLA " + str(RAM[PC+1]) )
            PC_next()
            value = RAM[PC]
            if status_C(accu - value, way='down'):
                accu += 256 - value
            else:
                accu -= value
            status_Z(accu)
        elif mnemo == 11:
            sv_inst.set("SUBRA " + str(RAM[PC+1]) )
            PC_next()
            value = RAM[RAM[PC]]
            if status_C(accu - value, way='down'):
                accu += 256 - value
            else:
                accu -= value
            status_Z(accu)
        elif mnemo == 12:
            sv_inst.set("ANDLA " + str(RAM[PC+1]) )
            PC_next()
            accu &= RAM[PC]
            status_Z(accu)
        elif mnemo == 13:
            sv_inst.set("ANDRA " + str(RAM[PC+1]) )
            PC_next()
            accu &= RAM[RAM[PC]]
            status_Z(accu)
        elif mnemo == 14:
            sv_inst.set("ORLA " + str(RAM[PC+1]) )
            PC_next()
            accu |= RAM[PC]
            status_Z(accu)
        elif mnemo == 15:
            sv_inst.set("ORRA " + str(RAM[PC+1]) )
            PC_next()
            accu |= RAM[RAM[PC]]
            status_Z(accu)
        elif mnemo == 16:
            sv_inst.set("XORLA " + str(RAM[PC+1]) )
            PC_next()
            accu ^= RAM[PC]
            status_Z(accu)
        elif mnemo == 17:
            sv_inst.set("XORRA " + str(RAM[PC+1]) )
            PC_next()
            accu ^= RAM[RAM[PC]]
            status_Z(accu)
        elif mnemo == 18:
            sv_inst.set("DECR " + str(RAM[PC+1]) )
            PC_next()
            address = RAM[PC]
            RAM[address]  = (-1 + RAM[address]) % 256
            status_Z(RAM[address])
        elif mnemo == 19:
            sv_inst.set("INCR " + str(RAM[PC+1]) )
            PC_next()
            address = RAM[PC]
            RAM[address]  = (1 + RAM[address]) % 256
            status_Z(RAM[address])
        elif mnemo == 20:
            sv_inst.set("DECRJZ " + str(RAM[PC+1]) )
            PC_next()
            address = RAM[PC]
            RAM[address] = (-1 + RAM[address]) % 256
            if status_Z(RAM[address]):
                PC += 2
        elif mnemo == 21:
            sv_inst.set("INCRJZ " + str(RAM[PC+1]) )
            PC_next()
            address = RAM[PC]
            RAM[address] = (1 + RAM[address]) % 256
            if status_Z(RAM[address]):
                PC += 2
        elif mnemo == 22:
            sv_inst.set("SHIFTRL " + str(RAM[PC+1]) )
            PC_next()
            address = RAM[PC]
            RAM[address] <<= 1 # shifts whitout taking care of the previous Carry bit
            carry = 1 if RAM[REG_STATUS] & 2 else 0 # gets the previous Carry bit on the status register
            RAM[address] += carry # sets the LSB equals to the previous Carry bit
            if status_C(RAM[address]):
                RAM[address] -= 256
        elif mnemo == 23:
            sv_inst.set("SHIFTRR " + str(RAM[PC+1]) )
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
            sv_inst.set("CBR " + str(RAM[PC+1]) + " " + str(RAM[PC+2]))
            PC_next()
            bit = RAM[PC]
            PC_next()
            RAM[RAM[PC]] &= (255-2**bit) # sets the specified bit to 0
        elif mnemo == 25:
            sv_inst.set("SBR " + str(RAM[PC+1]) + " " + str(RAM[PC+2]))
            PC_next()
            bit = RAM[PC]
            PC_next()
            RAM[RAM[PC]] |= 2**bit # sets the specified bit to 1
        elif mnemo == 26 or mnemo == 27:
            if mnemo == 26:
                sv_inst.set("BCRSC " + str(RAM[PC+1])+ " " + str(RAM[PC+2]) )
            else:
                sv_inst.set("BCRSS " + str(RAM[PC+1])+ " " + str(RAM[PC+2]) )
            PC_next()
            bit = RAM[PC]
            PC_next()
            if (mnemo == 26 and not(RAM[RAM[PC]] & 2**bit)) or (mnemo == 27 and (RAM[RAM[PC]] & 2**bit)):
                PC += 2
        elif mnemo == 28:
            sv_inst.set("JUMP " + str(RAM[PC+1]) )
            PC_next()
            PC = RAM[PC] - 1 # (-1) because of the "PC+1" after this actual execution
        elif mnemo == 29:
            sv_inst.set("CALL " + str(RAM[PC+1]) )
            PC_next()
            stack_in(PC)
            PC = RAM[PC] - 1 # (-1) because of the "PC+1 command" after this actual execution
        elif mnemo == 30:
            sv_inst.set("RETLA " + str(RAM[PC+1]) )
            PC_next()
            accu = RAM[PC]
            PC = stack_out() # to go back to the CALL
        elif mnemo == 31:
            sv_inst.set("RETURN" )
            PC = stack_out() # to go back to the CALL
        elif mnemo == 32:
            sv_inst.set("ADDRPC " + str(RAM[PC+1]) )
            PC_next()
            PC = (PC+RAM[RAM[PC]])%256
        elif mnemo == 33:
            sv_inst.set("INITSP" )
            SP = 0 # stack pointer
            OSP = 0
        elif mnemo == 34:
            sv_inst.set("RANDA" )
            accu = randint(0, 255)
        # Nouvelles instructions DGR2B
        elif mnemo == 35:
            sv_inst.set("COPYLI " + str(RAM[PC+1]) + " " + str(RAM[PC+2]) )
            PC_next()
            value = RAM[PC]
            PC_next()
            RAM[RAM[RAM[PC]]] = value
        elif mnemo == 36:
            sv_inst.set("COPYAI " + str(RAM[PC+1]) )
            PC_next()
            RAM[RAM[RAM[PC]]] = accu
        elif mnemo == 37:
            sv_inst.set("COPYIA " + str(RAM[PC+1]) )
            PC_next()
            accu = RAM[RAM[RAM[PC]]]
            status_Z(accu)
        elif mnemo == 38:
            sv_inst.set("COPYRI " + str(RAM[PC+1])+ " " + str(RAM[PC+2]) )
            PC_next()
            address = RAM[PC]
            PC_next()
            RAM[RAM[RAM[PC]]] = RAM[address]
            status_Z(RAM[address])
        elif mnemo == 39:
            sv_inst.set("COPYIR " + str(RAM[PC+1])+ " " + str(RAM[PC+2]) )
            PC_next()
            address = RAM[PC]
            PC_next()
            RAM[RAM[PC]] = RAM[RAM[address]]
            status_Z(RAM[RAM[address]])
        elif mnemo == 40:
            sv_inst.set("COPYII " + str(RAM[PC+1])+ " " + str(RAM[PC+2]) )
            PC_next()
            address = RAM[PC]
            PC_next()
            RAM[RAM[RAM[PC]]] = RAM[RAM[address]]
            status_Z(RAM[RAM[address]])
        elif mnemo == 41:
            sv_inst.set("SHIFTAL")
            accu <<= 1 # shifts whitout taking care of the previous Carry bit
            carry = 1 if RAM[REG_STATUS] & 2 else 0 # gets the previous Carry bit on the status register
            accu += carry # sets the LSB equals to the previous Carry bit
            if status_C(accu):
                accu -= 256
        elif mnemo == 42:
            sv_inst.set("SHIFTAR")
            carry = 1 if RAM[REG_STATUS] & 2 else 0 # gets the previous Carry bit on the status register
            if accu % 2 == 1: # if odd value => raises a new Carry
                RAM[REG_STATUS] |= 2 # sets Carry bit to 1
            else:
                RAM[REG_STATUS] &= 253 # sets Carry bit to 0
            accu >>= 1 # shifts whitout taking care of the previous Carry bit
            accu += 128 * carry # sets the MSB equals to the previous Carry bit
        elif mnemo == 43:
            sv_inst.set("JUMPI " + str(RAM[PC+1]) )
            PC_next()
            PC = RAM[RAM[PC]] - 1 # (-1) because of the "PC+1" after this actual execution
        elif mnemo == 44:
            sv_inst.set("CALLI " + str(RAM[PC+1]) )
            PC_next()
            stack_in(PC)
            PC = RAM[RAM[PC]] - 1 # (-1) because of the "PC+1 command" after this actual execution
        elif mnemo == 45:
            sv_inst.set("PUSH")
            if OSP >= OPSTACK_DEPTH:
                halt() # stack overflow
            opstack[OSP] = accu
            OSP += 1 
        elif mnemo == 46:
            sv_inst.set("POP")
            if OSP == 0:
                halt() # stack underflow
            else:
                OSP -= 1
                accu = opstack[OSP]
                status_Z(accu)
        elif mnemo == 47:
            sv_inst.set("PUSHR" + str(RAM[PC+1]))
            if OSP >= OPSTACK_DEPTH:
                halt() # stack overflow
            PC_next()
            address = RAM[PC]
            opstack[OSP] = RAM[address]
            OSP += 1 
        elif mnemo == 48:
            sv_inst.set("POPR" + str(RAM[PC+1]))
            PC_next()
            address = RAM[PC]
            if OSP == 0:
                halt() # stack underflow
            else:
                OSP -= 1
                RAM[address] = opstack[OSP]
                status_Z(RAM[address])
        elif mnemo == 49:
            sv_inst.set("PUSHI" + str(RAM[PC+1]))
            if OSP >= OPSTACK_DEPTH:
                halt() # stack overflow
            PC_next()
            address = RAM[PC]
            opstack[OSP] = RAM[RAM[address]]
            OSP += 1 
        elif mnemo == 50:
            sv_inst.set("POPI" + str(RAM[PC+1]))
            PC_next()
            address = RAM[PC]
            if OSP == 0:
                halt() # stack underflow
            else:
                OSP -= 1
                RAM[RAM[address]] = opstack[OSP]
                status_Z(RAM[RAM[address]])
        elif mnemo == 51:
            sv_inst.set("HEAD")
            if OSP == 0:
                halt() # stack underflow
            else:
                accu = opstack[OSP-1]
                status_Z(accu)
        elif mnemo == 52:
            sv_inst.set("DEPTH")
            accu = OSP
            status_Z(accu)
        else: # digirule program stops if unknown mnemonic
            execute(0) 
        
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
                btn_load['relief'] = tk.SUNKEN
        
    def save():
        """ sets the save_mode to save RAM to a program on the flash memory """
        global flash_memory, save_mode
        if not (run_mode or load_mode):
            print_dbg('action save')
            if not (run_mode or load_mode):
                save_mode = True
                btn_save['relief'] = tk.SUNKEN
        
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
            btn_load['relief'] = tk.RAISED
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
            btn_save['relief'] = tk.RAISED
        
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
        pause = 1 # pause (in s) between 2 executions on run_mode
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
