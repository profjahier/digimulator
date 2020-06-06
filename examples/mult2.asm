// Multiplier by Olivier Lecluse
// Input subroutine By Jaap Scherphuis
//
// press D0-D6 to enter a number in the data-leds
// press D7 to add it to the total in the address-leds

// Some handy constants
%define statusRegister      252
%define buttonRegister      253
%define timer               240
%define savedbuttons        241
%define prevbuttons         242
%define changedbuttons      243
%define n1                  255
%define n2low               244
%define n2high              245
%define reslow              254
%define reshigh             246

initsp
copylr 4 statusRegister
copylr 0 reslow             // result low
copylr 0 reshigh            // result high
copylr 0 n2high
copylr 0 buttonRegister
call input                  // asks for n1
copyar n2low
call input                  // asks for n2
copyar n1 
speed 128
nop
nop
nop
nop
nop

// Multiplication program : n1 x n2 -> res (16 bits)

:mult
      bcrsc 0 n1
      call addn             // adds n2 to res if n1 is odd
      cbr 1 statusRegister  // Clear carry
      shiftrr n1            // shifts n1 right
      cbr 1 statusRegister  // Clear carry
      shiftrl n2low         // shifts n2 left
      shiftrl n2high        // shifts n2 left
      copyla 255
      andra n1              // tests if n1 is zero
      bcrss 0 statusRegister 
      jump mult
      copyrr reshigh n1
:fin
      jump fin      
      nop
      nop
      nop
      nop
      nop


:addn
      copyra reslow
      addra n2low
      copyar reslow
      bcrsc 1 statusRegister
      incr reshigh
      copyra reshigh
      addra n2high
      copyar reshigh
      return
      nop
      nop
      nop
      nop
      nop

// Input numbers (d0-d6, d7 to exit)
// By Jaap Scherphuis

:input
      speed 16
      copylr 0 n1
      copylr 0 changedbuttons
      copylr 0 savedbuttons
      copylr 0 prevbuttons
      copylr 128 timer
      nop
      nop
      nop
:loop
      decrjz timer
      jump skiptoggle
      copylr 128 timer
      copyra n1
      xorla 128
      copyar n1
      nop
      nop
      nop
:skiptoggle
      copyra buttonRegister
      copyar savedbuttons
      copyra prevbuttons
      xorla 255
      andra savedbuttons
      copyar changedbuttons
      xorra n1
      andla 127
      copyar n1
      bcrss 7 changedbuttons
      jump skipadd
      return
      nop
      nop
      nop
:skipadd
      copyra savedbuttons
      copyar prevbuttons
      jump loop
      nop
      nop
      nop
