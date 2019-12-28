#! /usr/bin/python3
# Ronan Jahier
# Olivier Lecluse
# simulation de digirule 
# Licence CC-BY-NC-SA

import tkinter as tk
import tkinter.ttk as ttk
from random import randint
from converter import *

with open('config.txt', 'r', encoding='utf-8') as f:
    config = f.readlines()
COLOR_DATA_LED = config[0].split(',')[0]
COLOR_ADRESS_LED = config[1].split(',')[0]
COLOR_OFF = config[2].split(',')[0]

REG_STATUS = 252
REG_BUTTON = 253
REG_ADRESS = 254
REG_ADATA = 255

debug = False
view_ram = False

#
# Codage digirule
#

def print_dbg(*args,**kwargs):
    if debug:
        print(*args, **kwargs)

def PC_next():
    """ incrémente le PC, marque une pause (en fonction de la vitesse définie) et actualise l'affichage des LEDs """
    global PC, idle
    # On est libre pour traiter une instruction
    PC += 1
    # l'affichage sur LEDs adress est le contenu de RAM[REG_ADRESS] si le bit 2 du registre de status est à 1
    # sinon on affiche l'adresse du PC
    switch_led(RAM[REG_ADRESS], frame='adress') if RAM[REG_STATUS] & 4 else switch_led(PC, frame='adress') 
    switch_led(RAM[REG_ADATA], frame='data')
    if idle:
        idle = False
        can_adress.after(pause, PC_next1) # pause est en ms
def PC_next1():
    """ Pause is over !!"""
    global idle
    idle = True

def status_Z(n):
    """ gère le bit du Zéro pour le registre de status lorsque nécessaire """
    if n == 0:
         RAM[REG_STATUS] |= 1 # place le bit de zéro status à 1
         print_dbg('bit Z status = 1')
         return True
    print_dbg('bit Z status = 0')
    RAM[REG_STATUS] &= 254 # place le bit de zéro status à 0
    return False
    
def status_C(n, way='up'):
    """ gère le bit de Carry pour le registre de status lorsque nécessaire """
    if (n > 255 and way=='up') or (n < 0 and way=='down'):
        RAM[REG_STATUS] |= 2 # place le bit de carry status à 1
        print_dbg('bit C status = 1')
        return True
    RAM[REG_STATUS] &= 253 # place le bit de carry status à 0
    print_dbg('bit C status = 0')
    return False
            
def execute(mnemo):
    """exécute l'instruction du mnémonique mnemo (donné en décimal) """
    global run_mode, PC, pause, accu, SP, status_adr_is_0
    if mnemo == 0:
        sv_inst.set("HALT")
        run_mode = not(run_mode)
        can_run['bg'] = 'black'
        can_stop['bg'] = 'red'
    elif mnemo == 1:
        sv_inst.set("NOP")
        pass
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
        adress = RAM[PC]
        PC_next()
        RAM[RAM[PC]] = RAM[adress]
        status_Z(RAM[adress])
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
        adress = RAM[PC]
        RAM[adress]  = (-1 + RAM[adress]) % 256
        status_Z(RAM[adress])
    elif mnemo == 19:
        sv_inst.set("INCR " + str(RAM[PC+1]) )
        PC_next()
        adress = RAM[PC]
        RAM[adress]  = (1 + RAM[adress]) % 256
        status_Z(RAM[adress])
    elif mnemo == 20:
        sv_inst.set("DECRJZ " + str(RAM[PC+1]) )
        PC_next()
        adress = RAM[PC]
        RAM[adress] = (-1 + RAM[adress]) % 256
        if status_Z(RAM[adress]):
            PC += 2
    elif mnemo == 21:
        sv_inst.set("INCRJZ " + str(RAM[PC+1]) )
        PC_next()
        adress = RAM[PC]
        RAM[adress] = (1 + RAM[adress]) % 256
        if status_Z(RAM[adress]):
            PC += 2
    elif mnemo == 22:
        sv_inst.set("SHIFTRL " + str(RAM[PC+1]) )
        PC_next()
        adress = RAM[PC]
        RAM[adress] <<= 1 # décalage avant incorporation du bit Carry
        carry_actuelle = 1 if RAM[REG_STATUS] & 2 else 0
        RAM[adress] += carry_actuelle # ajoute le bit de Carry à droite (LSB)
        if status_C(RAM[adress]):
            RAM[adress] -= 256
    elif mnemo == 23:
        sv_inst.set("SHIFTRR " + str(RAM[PC+1]) )
        PC_next()
        adress = RAM[PC]
        carry_actuelle = 1 if RAM[REG_STATUS] & 2 else 0
        if RAM[adress] % 2 == 1: # nb impair => on "ejecte" un 1
            RAM[REG_STATUS] |= 2 # place le bit de carry status à 1
        else:
            RAM[REG_STATUS] &= 253 # place le bit de carry status à 0
        RAM[adress] >>= 1 # décalage avant incorporation du bit Carry
        RAM[adress] += 128 * carry_actuelle # ajoute le bit de Carry à gauche (MSB)
    elif mnemo == 24:
        sv_inst.set("CBR " + str(RAM[PC+1]) )
        PC_next()
        bit = RAM[PC]
        PC_next()
        RAM[RAM[PC]] &= (255-2**bit) # place le bit choisi à 0
    elif mnemo == 25:
        sv_inst.set("SBR " + str(RAM[PC+1]) )
        PC_next()
        bit = RAM[PC]
        PC_next()
        RAM[RAM[PC]] |= 2**bit # place le bit choisi à 1
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
        PC = RAM[PC] - 1 # (-1) parce qu'on fera PC+1 après avoir exécuté ce mnemo
    elif mnemo == 29:
        sv_inst.set("CALL " + str(RAM[PC+1]) )
        PC_next()
        SP = PC # pour savoir où revenir après un RETURN OU RETURNLA
        PC = RAM[PC] - 1 # (-1) parce qu'on fera PC+1 après avoir exécuté ce mnemo
    elif mnemo == 30:
        sv_inst.set("RETLA " + str(RAM[PC+1]) )
        PC_next()
        accu = RAM[PC]
        PC = SP # retour au CALL
    elif mnemo == 31:
        sv_inst.set("RETURN" )
        PC = SP # retour au CALL
    elif mnemo == 32:
        sv_inst.set("ADDRPC " + str(RAM[PC+1]) )
        PC_next()
        PC += RAM[PC]
    elif mnemo == 33:
        sv_inst.set("INITSP" )
        SP = 0 # stack pointer
    elif mnemo == 34:
        sv_inst.set("RANDA" )
        accu = randint(0, 255)
    else: # stop si mnemo inconnu
        execute(0) 
    
def programme_run():
    """ exécute le programme jusqu'à lire une instruction HALT 
    fetch - decode - execute """
    while run_mode: # si on n'a pas exécuté un HALT, on relance le cycle fetch-decode-execute
        if idle:
            mnemo = RAM[PC] # opcode
            display_ram()
            execute(mnemo)
            PC_next()
        can_adress.update()
        can_data.update()

def step():
    mnemo = RAM[PC] # opcode
    display_ram()
    execute(mnemo)
    PC_next()

def run():
    """ commute le mode run et lance l'exécution du programme à partir de l'adresse définie par les LEDs adress """
    global run_mode, PC, idle
    print_dbg(f'appui sur btn_run') 
    if run_mode and not(save_mode or load_mode):
        can_run['bg'] = 'black'
        can_stop['bg'] = 'red'
        run_mode = not(run_mode)
    elif not run_mode and not(save_mode or load_mode):
        can_run['bg'] = 'green'
        can_stop['bg'] = 'black'
        run_mode = not(run_mode)
        PC = b2d(read_from_led(frame='adress')) # adresse de la 1ère execute du programme à exécuter
        idle = True
        programme_run() # lancement du programme
        
def prev():
    """ passe à l'adresse précédente et affiche l'adresse en cours sur les LEDs adress 
    et le contenu de la RAM sur les LEDs data """
    global PC
    if not (run_mode or save_mode or load_mode):
        print_dbg('action prev')
        PC = 255 if PC == 0 else PC - 1
        print_dbg(f'PC={PC}')
        print_dbg(f'RAM[{PC}]={RAM[PC], d2b(RAM[PC])}')
        switch_led(PC, frame='adress')
        switch_led(RAM[PC], frame='data')
        display_ram()
    
def next_():
    """ passe à l'adresse suivante et affiche l'adresse en cours sur les LEDs adress 
    et le contenu de la RAM sur les LEDs data """
    global PC
    if not (run_mode or save_mode or load_mode):
        print_dbg('action next')
        PC = 0 if PC == 255 else PC + 1
        print_dbg(f'PC={PC}')
        print_dbg(f'RAM[{PC}]={RAM[PC], d2b(RAM[PC])}')
        switch_led(PC, frame='adress')
        switch_led(RAM[PC], frame='data')
        display_ram()
    
def goto():
    """ se rend à l'adresse définie par les LEDs data et affiche l'adresse en cours sur les LEDs adress 
    et le contenu de la RAM sur les LEDs data """
    global PC
    if not (run_mode or save_mode or load_mode):
        print_dbg('action goto')
        leds = read_from_led('data')
        PC = b2d(leds)
        print_dbg(f'PC={PC}')
        print_dbg(f'RAM[{PC}]={RAM[PC], d2b(RAM[PC])}')
        switch_led(PC, frame='adress')
        switch_led(RAM[PC], frame='data')
        display_ram()
    
def store():
    """ écrit l'état des LEDs data dans la RAM à l'adresse des LEDs adress 
    et passe à l'adresse suivante (next_) """
  #  global RAM
    if not (run_mode or save_mode or load_mode):
        print_dbg('action store')
        RAM[PC] = b2d(read_from_led('data'))
        print_dbg(RAM)
        next_()
        display_ram()
    
def load():
    """ charge un programme dans la RAM depuis la mémoire flash """
    global RAM, PC, load_mode
    if not (run_mode or save_mode):
        print_dbg('action load')
        if not (run_mode or save_mode):
            load_mode = True
            btn_load['relief'] = tk.SUNKEN
    
def save():
    """ sauvegarde la mémoire RAM dans un programme de la mémoire flash """
    global flash_memory, save_mode
    if not (run_mode or load_mode):
        print_dbg('action save')
        if not (run_mode or load_mode):
            save_mode = True
            btn_save['relief'] = tk.SUNKEN
    
def switch_led(n, frame='data', mode='int'):
    """ affiche le nb n sur les LEDs 
    mode = 'str' : le nb est écrit comme une chaine de 8 bits
    mode = 'int' : le nb est un entier """
    can = can_data if frame == 'data' else can_adress
    COLOR = COLOR_DATA_LED if frame == 'data' else COLOR_ADRESS_LED
    leds = n if mode == 'str' else d2b(n)
    for i,state in enumerate(leds):
        if state == '1':
            can.itemconfig('L'+str(7-i), fill=COLOR, outline=COLOR)
        else:
            can.itemconfig('L'+str(7-i), fill=COLOR_OFF, outline=COLOR_OFF)
        
def read_from_led(frame='data'):
    """ renvoie l'état des LEDs du frame 'data' ou 'adress' 
    sous la forme d'une chaine de 8 bits """
    can = can_data if frame == 'data' else can_adress
    color_ref = COLOR_DATA_LED if frame == 'data' else COLOR_ADRESS_LED
    leds = ''
    for i in range(8):
        COLOR = can.itemcget('L'+str(7-i), 'fill')
        if COLOR == color_ref:
            leds += '1'
        else:
            leds += '0'
    return leds
    
def led_switch(i, frame='data'):
    """ commute l'extinction ou l'allumage de la LED n°i """
    can = can_data if frame == 'data' else can_adress
    color_ref = COLOR_DATA_LED if frame == 'data' else COLOR_ADRESS_LED
    COLOR = can.itemcget('L'+str(i), 'outline')
    COLOR = color_ref if COLOR == COLOR_OFF else COLOR_OFF
    can.itemconfig('L'+str(i), fill=COLOR, outline=COLOR)
    
def btn_i(i):
    """ gestion de l'appui sur un bouton Data (dépend du mode en cours : run, load ou save) """
    global PC, load_mode, save_mode, flash_memory, RAZBtn
    print_dbg('press on btn'+str(i))

    if load_mode:   ### charge dans la RAM le programme n°i depuis la mémoire flash """
        with open('flash_memory.txt', 'r', encoding='utf-8') as f:
            flash_memory = f.readlines() 
        start = 256*i # debut de l'emplacement du prog n°i dans la mémoire flash
        for j in range(start, start+256):
            RAM[j-start] = int(flash_memory[j][:-1])
        print_dbg(RAM)         
        PC = 0
        RAM[REG_BUTTON] = 0
        load_mode = not load_mode
        btn_load['relief'] = tk.RAISED
        switch_led(PC, frame='adress')
        switch_led(RAM[PC], frame='data')
        
    elif save_mode: ### sauvegarde la mémoire RAM dans la mémoire flash
        start = 256*i # début de l'emplacement du prog n°i dans la mémoire flash
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
        led_switch(i, 'data')
        RAM[REG_BUTTON] ^= 2**i
    display_ram()

def btn_i_pressed(i):
    if run_mode: 
        RAM[REG_BUTTON] |= 2**i
        display_ram()
        print_dbg("press ", i)

def btn_i_released(i):
    if run_mode: 
        RAM[REG_BUTTON] &= 255-2**i
        display_ram()
        print_dbg("release ", i)

def reset():
    """ initialisation au lancement de l'application """
    global SP,PC, run_mode, RAM, flash_memory, pause, accu, load_mode, save_mode, idle
    pause = 1 # pause en secondes entre 2 instructions en mode run
    PC = 0 # program counter = adresse de RAM active
    SP = 0 # Stack Pointer
    switch_led(PC, frame='adress')
    run_mode, load_mode, save_mode = False, False, False
    RAM = [0]*256
    accu = 0 # registre accumulateur
    idle = True
    display_ram()
    with open('flash_memory.txt', 'r', encoding='utf-8') as f:
        flash_memory = f.readlines()

def change_speed(sender):
    global pause
    pause = speed_rule.get()
#
# debugger
#

def show_ram():
    global view_ram
    view_ram = not view_ram
    if view_ram:
        btn_dbg.configure(relief=tk.SUNKEN)
        display_ram()
    else:
        btn_dbg.configure(relief=tk.RAISED)
        text_RAM.config(state=tk.NORMAL)
        text_RAM.delete("1.0",tk.END)

def display_ram():
    if view_ram:
        text_RAM.config(state=tk.NORMAL)
        text_RAM.delete("1.0",tk.END)

        for l in range(32):
            line = d2h(l*8)+":  "
            for c in range(8):
                line += d2h(RAM[l*8+c])+" "
            if l != 31:
                line +="\n"
            text_RAM.insert(tk.END, line)
        
        lpc = PC // 8 + 1
        cpc = PC % 8 * 3 + 5
        text_RAM.mark_set("debut", "%d.%d"%(lpc,cpc))
        text_RAM.mark_set("fin", "%d.%d"%(lpc,cpc+2))
        text_RAM.tag_add("pc", "debut", "fin")
        text_RAM.config(state=tk.DISABLED)

    sv_acc.set(f"AC = {d2b(accu)} (dec : {str(accu)})")
    sv_pc.set(f"PC  =  {d2b(PC)} (hex : {d2h(PC)})")
    sv_sp.set(f"SP  =  {d2b(SP)} (hex : {d2h(SP)})")
    sv_status.set(f"ST  = {d2b(RAM[REG_STATUS])}")
    
def dbg_setpc(sender):
    global PC
    s = text_RAM.index(tk.CURRENT).split(".")
    l = int(s[0]) - 1
    c = (int(s[1]) - 5) // 3
    PC = l * 8 + c
    display_ram()

#
# Interface
#

    
digirule = tk.Tk()
digirule.title("DIGIMULATOR : simulateur de digirule 2A")
frame_dr = tk.Frame(digirule)
frame_dr.pack(side=tk.LEFT)
frame_dbg = tk.Frame(digirule)
frame_dbg.pack(side=tk.LEFT)

frame_reg = tk.Frame(frame_dbg)
frame_reg.pack(side=tk.TOP)
frame_ram = tk.Frame(frame_dbg)
frame_ram.pack()

# Interface digirule
frame_run= tk.Frame(frame_dr)
frame_run.pack()
btn_run = tk.Button(frame_run, text='Run/Stop ', command=run)
btn_run.pack(side=tk.LEFT)
btn_step = tk.Button(frame_run, text='Step ', command=step)
btn_step.pack(side=tk.LEFT)
frame_state = tk.Frame(frame_run)
frame_state.pack(side=tk.LEFT)
can_run = tk.Canvas(frame_state, width=30, height=10, bg='black')
can_run.pack(side=tk.TOP)
can_stop = tk.Canvas(frame_state, width=30, height=10, bg='red')
can_stop.pack(side=tk.BOTTOM)
btn_dbg = tk.Button(frame_run, text='View RAM ', command=show_ram)
btn_dbg.pack(side=tk.LEFT)
frame_goto = tk.Frame(frame_dr)
frame_goto.pack()
ttk.Button(frame_goto, text='Goto', command=goto).pack(side=tk.LEFT)
ttk.Button(frame_goto, text='Prev.', command=prev).pack(side=tk.LEFT)
ttk.Button(frame_goto, text='Next', command=next_).pack(side=tk.LEFT)
ttk.Button(frame_goto, text='Store', command=store).pack(side=tk.LEFT)
frame_file = tk.Frame(frame_dr)
frame_file.pack()
btn_load = tk.Button(frame_file, text='Load', command=load)
btn_load.pack(side=tk.LEFT)
btn_save = tk.Button(frame_file, text='Save', command=save)
btn_save.pack(side=tk.LEFT)
speed_rule = tk.Scale(frame_dr, from_=0, to=1000, orient=tk.HORIZONTAL, length=300, command=change_speed)
speed_rule.pack()
frame_adress = tk.Frame(frame_dr)
frame_adress.pack()
can_adress = tk.Canvas(frame_dr, width=340, height=40, background='white')
can_adress.pack()
for i in range(8):
    can_adress.create_oval((20*(2*i+1)), 10, (20*(2*i+2)), 30, outline=COLOR_ADRESS_LED, fill=COLOR_ADRESS_LED, tags='L'+str(7-i))

frame_data = tk.Frame(frame_dr)
frame_data.pack()
can_data = tk.Canvas(frame_dr, width=340, height=40, background='white')
can_data.pack()
for i in range(8):
    can_data.create_oval((20*(2*i+1)), 10, (20*(2*i+2)), 30, outline=COLOR_DATA_LED, fill=COLOR_DATA_LED, tags='L'+str(7-i))

frame_btn = tk.Frame(frame_dr, width=340)
frame_btn.pack()
for i in range(7,-1,-1):
    btn = ttk.Button(frame_btn, text=str(i), width=4, command=lambda i=i:btn_i(i))
    btn.pack(side=tk.LEFT)
    btn.bind("<ButtonPress>", lambda sender, i=i:btn_i_pressed(i))
    btn.bind("<ButtonRelease>", lambda sender, i=i:btn_i_released(i))

# Interface debugger

sv_acc = tk.StringVar()
sv_status = tk.StringVar()
sv_pc = tk.StringVar()
sv_sp = tk.StringVar()
sv_inst = tk.StringVar()

label_sp = tk.Label(frame_reg, textvariable=sv_sp)
label_sp.pack()
label_pc = tk.Label(frame_reg, textvariable=sv_pc)
label_pc.pack()
label_inst = tk.Label(frame_reg, textvariable=sv_inst, background="yellow")
label_inst.pack()

label_acc = tk.Label(frame_reg, textvariable=sv_acc)
label_acc.pack()

label_status = tk.Label(frame_reg, textvariable=sv_status)
label_status.pack()

text_RAM = tk.Text(frame_dbg, width=32, height=32, bg='white')
text_RAM.tag_config("pc", background="yellow")
text_RAM.bind("<Double-Button-1>", dbg_setpc)
text_RAM.pack()

ttk.Button(frame_dr, text='Quit', command=digirule.destroy).pack()

reset() # initialisation au lancement de l'application
digirule.mainloop()

