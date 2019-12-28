#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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


def d2h(d):
    """ convertit un entier en une chaine de 2 caractères hexadécimaux 
     entrée : d = nb entier (base décimale)
     sortie : chaine de 2 caractères ('0' à 'F')  """
    return hex(d)[2:].rjust(2, '0')
