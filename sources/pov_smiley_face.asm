// This program will scroll through a sequence of 8 bytes which contains
// the information to draw an 8x8 smiley face. The information is sent to the
// 8 data LED's and when the Digirule is waved in the air (in a dark - or 
// semi-dark room) you will see a smiley face been drawn in the air.
// NOTE: when you run the program, you will need to turn the address LED's off
// by pressing the 'goto' button.

// Constants
%define numberToAddToProgramCounter 240
%define statusRegister      252
%define buttonRegister      253
%define addressLEDRegister  254
%define dataLEDRegister     255

// Setup (this code runs once)
initsp
speed 1
copylr 0 numberToAddToProgramCounter

// Main loop (this code runs repeatedly until power is removed) 
:Loop
call SmileyFaceData
copyar dataLEDRegister
copyra numberToAddToProgramCounter
addla 2
copyar numberToAddToProgramCounter
jump loop

// Padding
nop
nop
nop
nop
nop
nop
nop
nop
nop
nop
nop
nop
nop
nop

:SmileyFaceData
addrpc numberToAddToProgramCounter
retla 126
retla 129
retla 165
retla 129
retla 165
retla 153
retla 129
retla 126
nop
copylr 0 numberToAddToProgramCounter
jump SmileyFaceData    
