// Adder
// By Jaap Scherphuis
//
// press D0-D6 to enter a number in the data-leds
// press D7 to add it to the total in the address-leds

// Some handy constants
%define statusRegister      252
%define buttonRegister      253
%define addressLEDRegister  254
%define dataLEDRegister     255
%define timer 240
%define savedbuttons 241
%define prevbuttons 242
%define changedbuttons 243

// My App
      speed 16
      copylr 4 statusRegister
      copylr 0 addressLEDRegister
      copylr 0 dataLEDRegister
      copylr 128 timer
:loop
      decrjz timer
      jump skiptoggle
      copylr 128 timer
      copyra dataLEDRegister
      xorla 128
      copyar dataLEDRegister
:skiptoggle
      copyra buttonRegister
      copyar savedbuttons
      copyra prevbuttons
      xorla 255
      andra savedbuttons
      copyar changedbuttons
      xorra dataLEDRegister
      andla 127
      copyar dataLEDRegister
      bcrss 7 changedbuttons
      jump skipadd
      addra addressLEDRegister
      copyar addressLEDRegister
:skipadd
      copyra savedbuttons
      copyar prevbuttons
      jump loop
