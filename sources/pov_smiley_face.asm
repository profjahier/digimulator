// This program will scroll through a sequence of 8 bytes which contains
// the information to draw an 8x8 smiley face. The information is sent to the
// 8 data LED's and when the Digirule is waved in the air (in a dark - or 
// semi-dark room) you will see a smiley face been drawn in the air.

//
// This version uses the Digirule 2B instruction set and uses indirect adressing.
//

// Constants
%define index           240
%define lineadr         241
%define output          242
%define statusRegister  252
%define dataLEDRegister 255
%define hideAddressBit  2

	initsp
	speed 1
	copylr dataLEDRegister output
	sbr hideAddressBit statusRegister
:mainloop
	copylr 8 index
	copylr POV lineadr
:loop
	copyii lineadr output
	incr lineadr
	decrjz index
	jump loop
	jump mainloop


// Drawing
%data POV 126 129 165 129 165 153 129 126