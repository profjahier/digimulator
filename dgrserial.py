# Module handling serial communication with the digirule

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
