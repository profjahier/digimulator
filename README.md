# digimulator
Simulator of **digirule 2** (https://bradsprojects.com/digirule2/) written in Python (by roro &amp; wawa)

# Instruction set

Digimulator offers the *Digirule 2B* enhanced instruction set. See https://github.com/wawachief/DGR2B for more informations.

# Assembler Quick guide

## Assembler special commands

- **%define** : defines constants. Usage : `%define NAME VALUE`
```
// Constants
%define statusRegister  252
%define dataLEDRegister 255
%define hideAddressBit  2
```
- **%data** : inserts one or many bytes in the code. Usage : `%data NAME byte1 byte2 ... byten`
```
// Variables declarations
%data index 0
%data lineadr 0

// Drawing
%data POV 126 129 165 129 165 153 129 126
```

## Labels
Labels begin with `:`.
```
:loop
	copyir lineadr dataLEDRegister
	incr lineadr
	decrjz index
	jump loop
```
## Comments

Comments begin with `//`

## Numbers 

Numbers are 8 bits long and can be in decimal (`127` for example) or in binary , beginning with `0b` (`0b11110101` for example).

<img src="licence.png" alt="licence CC-BY-NC-SA" height="30"/>

