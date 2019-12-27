#! /home/profjahier/anaconda3/bin/python
# Ronan Jahier & Olivier Lécluse
# Version sans sleep et modif boutons
# simulation de digirule 

import tkinter as tk
import tkinter.ttk as ttk
#import time
from random import randint
from mes_outils import *

with open('config.txt', 'r', encoding='utf-8') as f:
    config = f.readlines()
COULEUR_DATA_LED = config[0].split(',')[0]
COULEUR_ADRESS_LED = config[1].split(',')[0]
COULEUR_ETEINT = config[2].split(',')[0]

ADR_STATUS = 252
ADR_BUTTON = 253
ADR_ADRESS = 254
ADR_DATA = 255

DEBUG=True

def print_dbg(*args,**kwargs):
    if DEBUG:
        print(*args, **kwargs)

def PC_next():
    """ incrémente le PC, marque une pause (en fonction de la vitesse définie) et actualise l'affichage des LEDs 
    version non bloquante : on enleve le sleep !"""
    global PC, idle
    # On est libre pour traiter une instruction
    PC += 1
    # l'affichage sur LEDs adress est le contenu de RAM[ADR_ADRESS] si le bit 2 du registre de status est à 1
    # sinon on affiche l'adresse du PC
    affiche_led(RAM[ADR_ADRESS], frame='adress') if RAM[ADR_STATUS] & 4 else affiche_led(PC, frame='adress') 
    affiche_led(RAM[ADR_DATA], frame='data')
    if idle:
        idle = False
        can_adress.after(pause, PC_next1) # pause est en ms
def PC_next1():
    """La pause est finie !!"""
    global idle
    idle = True

def status_Z(n):
    """ gère le bit du Zéro pour le registre de status lorsque nécessaire """
    if n == 0:
         RAM[ADR_STATUS] |= 1 # place le bit de zéro status à 1
         print_dbg('bit Z status = 1')
         return True
    print_dbg('bit Z status = 0')
    RAM[ADR_STATUS] &= 254 # place le bit de zéro status à 0
    return False
    
def status_C(n, sens='sup'):
    """ gère le bit de Carry pour le registre de status lorsque nécessaire """
    if (n > 255 and sens=='sup') or (n < 0 and sens=='inf'):
        RAM[ADR_STATUS] |= 2 # place le bit de carry status à 1
        print_dbg('bit C status = 1')
        return True
    RAM[ADR_STATUS] &= 253 # place le bit de carry status à 0
    print_dbg('bit C status = 0')
    return False
            
def execute(mnemo):
    """exécute l'instruction du mnémonique mnemo (donné en décimal) """
    global run_mode, PC, pause, accu, SP, status_adr_is_0
    if mnemo == 0:
        print_dbg('HALT')
        run_mode = not(run_mode)
        can_run['bg'] = 'black'
        can_stop['bg'] = 'red'
    elif mnemo == 1:
        print_dbg('NOP')
        pass
    elif mnemo == 2:
        print_dbg('SPEED', end=' ')
        PC_next()
        print_dbg(RAM[PC])
        pause = 1 + 2 * RAM[PC] 
    elif mnemo == 3:
        print_dbg('COPYLR', end=' ')
        PC_next()
        print_dbg(RAM[PC], end=' ')
        valeur = RAM[PC]
        PC_next()
        print_dbg(RAM[PC])
        RAM[RAM[PC]] = valeur
    elif mnemo == 4:
        print_dbg('COPYLA', end=' ')
        PC_next()
        print_dbg(RAM[PC])
        accu = RAM[PC]
        print_dbg(f"accu = {accu}")
    elif mnemo == 5:
        print_dbg('COPYAR', end=' ')
        PC_next()
        print_dbg(RAM[PC])
        RAM[RAM[PC]] = accu
        print_dbg(f"accu = {accu}")
    elif mnemo == 6:
        print_dbg('COPYRA', end=' ')
        PC_next()
        print_dbg(RAM[PC])
        accu = RAM[RAM[PC]]
        status_Z(accu)
        print_dbg(f"accu = {accu}")
    elif mnemo == 7:
        print_dbg('COPYRR', end=' ')
        PC_next()
        print_dbg(RAM[PC], end=' ')
        adresse = RAM[PC]
        PC_next()
        print_dbg(RAM[PC])
        RAM[RAM[PC]] = RAM[adresse]
        status_Z(RAM[adresse])
    elif mnemo == 8:
        print_dbg('ADDLA', end=' ')
        PC_next()
        print_dbg(RAM[PC])
        valeur = RAM[PC]        
        if status_C(accu + valeur):
            accu += valeur - 256
        else:
            accu += valeur
        status_Z(accu)
        print_dbg(f"accu = {accu}")
    elif mnemo == 9:
        print_dbg('ADDRA', end=' ')
        PC_next()
        print_dbg(RAM[PC])
        valeur = RAM[RAM[PC]]
        if status_C(accu + valeur):
            accu += valeur - 256
        else:
            accu += valeur
        status_Z(accu)
        print_dbg(f"accu = {accu}")
    elif mnemo == 10:
        print_dbg('SUBLA', end=' ')
        PC_next()
        print_dbg(RAM[PC])
        valeur = RAM[PC]
        if status_C(accu - valeur, sens='inf'):
            accu += 256 - valeur
        else:
            accu -= valeur
        status_Z(accu)
        print_dbg(f"accu = {accu}")
    elif mnemo == 11:
        print_dbg('SUBRA', end=' ')
        PC_next()
        print_dbg(RAM[PC])
        valeur = RAM[RAM[PC]]
        if status_C(accu - valeur, sens='inf'):
            accu += 256 - valeur
        else:
            accu -= valeur
        status_Z(accu)
        print_dbg(f"accu = {accu}")
    elif mnemo == 12:
        print_dbg('ANDLA', end=' ')
        PC_next()
        print_dbg(RAM[PC])
        accu &= RAM[PC]
        status_Z(accu)
        print_dbg(f"accu = {accu}")
    elif mnemo == 13:
        print_dbg('ANDRA', end=' ')
        PC_next()
        print_dbg(RAM[PC])
        accu &= RAM[RAM[PC]]
        status_Z(accu)
        print_dbg(f"accu = {accu}")
    elif mnemo == 14:
        print_dbg('ORLA', end=' ')
        PC_next()
        print_dbg(RAM[PC])
        accu |= RAM[PC]
        status_Z(accu)
        print_dbg(f"accu = {accu}")
    elif mnemo == 15:
        print_dbg('ORRA', end=' ')
        PC_next()
        print_dbg(RAM[PC])
        accu |= RAM[RAM[PC]]
        status_Z(accu)
        print_dbg(f"accu = {accu}")
    elif mnemo == 16:
        print_dbg('XORLA', end=' ')
        PC_next()
        print_dbg(RAM[PC])
        accu ^= RAM[PC]
        status_Z(accu)
        print_dbg(f"accu = {accu}")
    elif mnemo == 17:
        print_dbg('XORRA', end=' ')
        PC_next()
        print_dbg(RAM[PC])
        accu ^= RAM[RAM[PC]]
        status_Z(accu)
        print_dbg(f"accu = {accu}")
    elif mnemo == 18:
        print_dbg('DECR', end=' ')
        PC_next()
        print_dbg(RAM[PC])
        adresse = RAM[PC]
        RAM[adresse]  = (-1 + RAM[adresse]) % 256
        status_Z(RAM[adresse])
    elif mnemo == 19:
        print_dbg('INCR', end=' ')
        PC_next()
        print_dbg(RAM[PC])
        adresse = RAM[PC]
        RAM[adresse]  = (1 + RAM[adresse]) % 256
        status_Z(RAM[adresse])
    elif mnemo == 20:
        print_dbg('DECRJZ', end=' ')
        PC_next()
        print_dbg(RAM[PC])
        adresse = RAM[PC]
        RAM[adresse] = (-1 + RAM[adresse]) % 256
        if status_Z(RAM[adresse]):
            PC += 2
    elif mnemo == 21:
        print_dbg('INCRJZ', end=' ')
        PC_next()
        print_dbg(RAM[PC])
        adresse = RAM[PC]
        RAM[adresse] = (1 + RAM[adresse]) % 256
        if status_Z(RAM[adresse]):
            PC += 2
    elif mnemo == 22:
        print_dbg('SHIFTRL', end=' ')
        PC_next()
        print_dbg(RAM[PC])
        adresse = RAM[PC]
        RAM[adresse] <<= 1 # décalage avant incorporation du bit Carry
        carry_actuelle = 1 if RAM[ADR_STATUS] & 2 else 0
        print_dbg(f'carry actuelle = {carry_actuelle}')
        RAM[adresse] += carry_actuelle # ajoute le bit de Carry à droite (LSB)
        if status_C(RAM[adresse]):
            RAM[adresse] -= 256
    elif mnemo == 23:
        print_dbg('SHIFTRR', end=' ')
        PC_next()
        print_dbg(RAM[PC])
        adresse = RAM[PC]
        carry_actuelle = 1 if RAM[ADR_STATUS] & 2 else 0
        print_dbg(f'carry actuelle = {carry_actuelle}')
        if RAM[adresse] % 2 == 1: # nb impair => on "ejecte" un 1
            RAM[ADR_STATUS] |= 2 # place le bit de carry status à 1
            print_dbg('bit C status = 1')
        else:
            RAM[ADR_STATUS] &= 253 # place le bit de carry status à 0
            print_dbg('bit C status = 0')
        RAM[adresse] >>= 1 # décalage avant incorporation du bit Carry
        RAM[adresse] += 128 * carry_actuelle # ajoute le bit de Carry à gauche (MSB)
    elif mnemo == 24:
        print_dbg('CBR', end=' ')
        PC_next()
        print_dbg(RAM[PC], end=' ')
        bit = RAM[PC]
        PC_next()
        print_dbg(RAM[PC])
        RAM[RAM[PC]] &= (255-2**bit) # place le bit choisi à 0
    elif mnemo == 25:
        print_dbg('SBR', end=' ')
        PC_next()
        print_dbg(RAM[PC], end= ' ')
        bit = RAM[PC]
        PC_next()
        print_dbg(RAM[PC])
        RAM[RAM[PC]] |= 2**bit # place le bit choisi à 1
    elif mnemo == 26 or mnemo == 27:
        if mnemo == 26:
            print_dbg('BCRSC', end=' ')
        else:
            print_dbg('BCRSS', end=' ')
        PC_next()
        print_dbg(RAM[PC], end= ' ')
        bit = RAM[PC]
        PC_next()
        print_dbg(RAM[PC])
        if (mnemo == 26 and not(RAM[RAM[PC]] & 2**bit)) or (mnemo == 27 and (RAM[RAM[PC]] & 2**bit)):
            PC += 2
    elif mnemo == 28:
        print_dbg('JUMP', end=' ')
        PC_next()
        print_dbg(RAM[PC])
        PC = RAM[PC] - 1 # (-1) parce qu'on fera PC+1 après avoir exécuté ce mnemo
    elif mnemo == 29:
        print_dbg('CALL', end=' ')
        PC_next()
        print_dbg(RAM[PC])
        SP = PC # pour savoir où revenir après un RETURN OU RETURNLA
        PC = RAM[PC] - 1 # (-1) parce qu'on fera PC+1 après avoir exécuté ce mnemo
    elif mnemo == 30:
        print_dbg('RETLA', end=' ')
        PC_next()
        print_dbg(RAM[PC])
        accu = RAM[PC]
        PC = SP # retour au CALL
        print_dbg(f"accu = {accu}")
    elif mnemo == 31:
        print_dbg('RETURN')
        PC = SP # retour au CALL
    elif mnemo == 32:
        print_dbg('ADDRPC', end=' ')
        PC_next()
        print_dbg(RAM[PC])
        PC += RAM[PC]
    elif mnemo == 33:
        print_dbg('INITSP')
        SP = 0 # stack pointer
    elif mnemo == 34:
        print_dbg('RANDA')
        accu = randint(0, 255)
        print_dbg(f"accu = {accu}")
    else: # stop si mnemo inconnu
        execute(0) 
    
def programme_run():
    """ exécute le programme jusqu'à lire une instruction HALT 
    fetch - decode - execute """
    global PC
    while run_mode: # si on n'a pas exécuté un HALT, on relance le cycle fetch-decode-execute
        if idle:
            mnemo = RAM[PC] # opcode
            execute(mnemo)
            print_dbg(RAM)
            PC_next()
        can_adress.update()
        can_data.update()

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
        PC = b2d(lecture_led(frame='adress')) # adresse de la 1ère instruction du programme à exécuter
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
        affiche_led(PC, frame='adress')
        affiche_led(RAM[PC], frame='data')
    
def next_():
    """ passe à l'adresse suivante et affiche l'adresse en cours sur les LEDs adress 
    et le contenu de la RAM sur les LEDs data """
    global PC
    if not (run_mode or save_mode or load_mode):
        print_dbg('action next')
        PC = 0 if PC == 255 else PC + 1
        print_dbg(f'PC={PC}')
        print_dbg(f'RAM[{PC}]={RAM[PC], d2b(RAM[PC])}')
        affiche_led(PC, frame='adress')
        affiche_led(RAM[PC], frame='data')
    
def goto():
    """ se rend à l'adresse définie par les LEDs data et affiche l'adresse en cours sur les LEDs adress 
    et le contenu de la RAM sur les LEDs data """
    global PC
    if not (run_mode or save_mode or load_mode):
        print_dbg('action goto')
        leds = lecture_led('data')
        PC = b2d(leds)
        print_dbg(f'PC={PC}')
        print_dbg(f'RAM[{PC}]={RAM[PC], d2b(RAM[PC])}')
        affiche_led(PC, frame='adress')
        affiche_led(RAM[PC], frame='data')
    
def store():
    """ écrit l'état des LEDs data dans la RAM à l'adresse des LEDs adress 
    et passe à l'adresse suivante (next_) """
  #  global RAM
    if not (run_mode or save_mode or load_mode):
        print_dbg('action store')
        RAM[PC] = b2d(lecture_led('data'))
        print_dbg(RAM)
        next_()
    
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
    global memoire_flash, save_mode
    if not (run_mode or load_mode):
        print_dbg('action save')
        if not (run_mode or load_mode):
            save_mode = True
            btn_save['relief'] = tk.SUNKEN
    
def affiche_led(n, frame='data', mode='int'):
    """ affiche le nb n sur les LEDs 
    mode = 'str' : le nb est écrit comme une chaine de 8 bits
    mode = 'int' : le nb est un entier """
    can = can_data if frame == 'data' else can_adress
    couleur = COULEUR_DATA_LED if frame == 'data' else COULEUR_ADRESS_LED
    leds = n if mode == 'str' else d2b(n)
    for i,etat in enumerate(leds):
        if etat == '1':
            can.itemconfig('L'+str(7-i), fill=couleur, outline=couleur)
        else:
            can.itemconfig('L'+str(7-i), fill=COULEUR_ETEINT, outline=COULEUR_ETEINT)
        
def lecture_led(frame='data'):
    """ renvoie l'état des LEDs du frame 'data' ou 'adress' 
    sous la forme d'une chaine de 8 bits """
    can = can_data if frame == 'data' else can_adress
    couleur_ref = COULEUR_DATA_LED if frame == 'data' else COULEUR_ADRESS_LED
    leds = ''
    for i in range(8):
        couleur = can.itemcget('L'+str(7-i), 'fill')
        if couleur == couleur_ref:
            leds += '1'
        else:
            leds += '0'
    return leds
    
def led_change(i, frame='data'):
    """ commute l'extinction ou l'allumage de la LED n°i """
    can = can_data if frame == 'data' else can_adress
    couleur_ref = COULEUR_DATA_LED if frame == 'data' else COULEUR_ADRESS_LED
    couleur = can.itemcget('L'+str(i), 'outline')
    couleur = couleur_ref if couleur == COULEUR_ETEINT else COULEUR_ETEINT
    can.itemconfig('L'+str(i), fill=couleur, outline=couleur)
    
def btn_i(i):
    """ gestion de l'appui sur un bouton Data (dépend du mode en cours : run, load ou save) """
    global PC, load_mode, save_mode, memoire_flash, RAZBtn
    print_dbg('appui sur btn'+str(i))

    if load_mode:   ### charge dans la RAM le programme n°i depuis la mémoire flash """
        with open('memoire_flash.txt', 'r', encoding='utf-8') as f:
            memoire_flash = f.readlines() 
        debut = 256*i # debut de l'emplacement du prog n°i dans la mémoire flash
        for j in range(debut, debut+256):
            RAM[j-debut] = int(memoire_flash[j][:-1])
        print_dbg(RAM)         
        PC = 0
        RAM[ADR_BUTTON] = 0
        load_mode = not load_mode
        btn_load['relief'] = tk.RAISED
        affiche_led(PC, frame='adress')
        affiche_led(RAM[PC], frame='data')
        
    elif save_mode: ### sauvegarde la mémoire RAM dans la mémoire flash
        debut = 256*i # debut de l'emplacement du prog n°i dans la mémoire flash
        with open('memoire_flash.txt', 'w', encoding='utf-8') as f:
            for j in range(0, debut):
                f.write(memoire_flash[j])
            for j in range(debut, debut + 256):
                f.write(str(RAM[j-debut])+'\n')
            for j in range(debut + 256, len(memoire_flash)):
                f.write(memoire_flash[j])
        save_mode = not save_mode
        btn_save['relief'] = tk.RAISED
    
    elif run_mode: 
        pass
        # RAM[ADR_BUTTON] ^= 2**i
    else:
        led_change(i, 'data')
        RAM[ADR_BUTTON] ^= 2**i

def btn_i_pressed(i):
    if run_mode: 
        RAM[ADR_BUTTON] |= 2**i
        print_dbg("press ", i)

def btn_i_released(i):
    if run_mode: 
        RAM[ADR_BUTTON] &= 255-2**i
        print_dbg("release ", i)

def reset():
    """ initialisation au lancement de l'application """
    global PC, run_mode, RAM, memoire_flash, pause, accu, load_mode, save_mode, idle
    pause = 1 # pause en secondes entre 2 instructions en mode run
    PC = 0 # program counter = adresse de RAM active
    affiche_led(PC, frame='adress')
    run_mode, load_mode, save_mode = False, False, False
    RAM = [0]*256
    accu = 0 # registre accumulateur
    idle = True
    with open('memoire_flash.txt', 'r', encoding='utf-8') as f:
        memoire_flash = f.readlines()

    
digirule = tk.Tk()
digirule.title("Digirule (simulateur)")

frame_run= tk.Frame(digirule)
frame_run.pack()
btn_run = tk.Button(frame_run, text='Run/Stop ', command=run)
btn_run.pack(side=tk.LEFT)
frame_etat = tk.Frame(frame_run)
frame_etat.pack(side=tk.LEFT)
can_run = tk.Canvas(frame_etat, width=30, height=10, bg='black')
can_run.pack(side=tk.TOP)
can_stop = tk.Canvas(frame_etat, width=30, height=10, bg='red')
can_stop.pack(side=tk.BOTTOM)
frame_goto = tk.Frame(digirule)
frame_goto.pack()
ttk.Button(frame_goto, text='Goto', command=goto).pack(side=tk.LEFT)
ttk.Button(frame_goto, text='Prev.', command=prev).pack(side=tk.LEFT)
ttk.Button(frame_goto, text='Next', command=next_).pack(side=tk.LEFT)
ttk.Button(frame_goto, text='Store', command=store).pack(side=tk.LEFT)
frame_file = tk.Frame(digirule)
frame_file.pack()
btn_load = tk.Button(frame_file, text='Load', command=load)
btn_load.pack(side=tk.LEFT)
btn_save = tk.Button(frame_file, text='Save', command=save)
btn_save.pack(side=tk.LEFT)

frame_adress = tk.Frame(digirule)
frame_adress.pack()
can_adress = tk.Canvas(digirule, width=340, height=40, background='white')
can_adress.pack()
for i in range(8):
    can_adress.create_oval((20*(2*i+1)), 10, (20*(2*i+2)), 30, outline=COULEUR_ADRESS_LED, fill=COULEUR_ADRESS_LED, tags='L'+str(7-i))

frame_data = tk.Frame(digirule)
frame_data.pack()
can_data = tk.Canvas(digirule, width=340, height=40, background='white')
can_data.pack()
for i in range(8):
    can_data.create_oval((20*(2*i+1)), 10, (20*(2*i+2)), 30, outline=COULEUR_DATA_LED, fill=COULEUR_DATA_LED, tags='L'+str(7-i))

frame_btn = tk.Frame(digirule, width=340)
frame_btn.pack()
for i in range(7,-1,-1):
    btn = ttk.Button(frame_btn, text=str(i), width=4, command=lambda i=i:btn_i(i))
    btn.pack(side=tk.LEFT)
    btn.bind("<ButtonPress>", lambda sender, i=i:btn_i_pressed(i))
    btn.bind("<ButtonRelease>", lambda sender, i=i:btn_i_released(i))


# text_RAM = tk.Text(digirule, width=40, height=32, bg='white')
# text_RAM.pack()

ttk.Button(digirule, text='Quitter', command=digirule.destroy).pack()

reset() # initialisation au lancement de l'application
digirule.mainloop()

