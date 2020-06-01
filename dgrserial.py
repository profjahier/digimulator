# Module handling serial communication with the digirule

import serial
import serial.tools.list_ports as list_ports
from tkinter import simpledialog, messagebox

TIMEOUT = 0.1 # Detection port serie

def comport(baud, mainWindow, port=""):
    ''' return a serial port '''
    ser_port = serial.Serial(timeout=TIMEOUT)
    ser_port.baudrate = baud
    if port != "":
        ser_port.port = port
    else:
        ports = list_ports.comports()
        serial_devices = ""
        for i,p in enumerate(ports):
            serial_devices += str(i) + " : " + p.device + "\n"
        # print(len(ports), 'ports found')
        if len(ports)>1:
            # Multiple adapters detected, ask the user
            serial_devices += "\nEnter the number of the device connected to Digirule"
            answer = simpledialog.askstring("Choose your Serial adapter", serial_devices,
                                    parent=mainWindow)
            try:
                ser_port.port = ports[int(answer)].device
            except:
                ser_port.port = ports[0].device
        elif len(ports) == 1:
            # We choose the only adapter present
                ser_port.port = ports[0].device
        else:
            # No serial port detected
            messagebox.showerror("Error", "No serial adapter detected")
            return None
    return ser_port

def ram2hex(ram):
    """converts the content of the ram info hex format"""
    def tohex(i):
        """converts an integer into hexadecimal on 2 caracters
        ex : tohex(8) -> '08' ; tohex(12) -> '0C'
        """
        return hex(i)[2:].rjust(2,'0').upper()

    hexdump = ""
    for line in range(16):
        nbcol = 12 if line == 15 else 16
        # Line header : nbcol (2 bytes) + address (2 bytes)
        newline = ':' + tohex(nbcol) + '00' + tohex(line * 16) + '00'
        control = nbcol + line * nbcol
        for col in range(nbcol):
            r = ram[line*16+col]
            control += r
            newline += tohex(r)
        newline += tohex((256-control)%256)
        hexdump += newline + '\n'
    hexdump += ":00000001FF"
    return hexdump
