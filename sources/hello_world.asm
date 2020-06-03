%define statusReg 0b11111100
%define zeroFlag  0

speed 128
initsp
copylr 0 index
:loop
    copyla hw
    addra index
    copyar cpy_from
    call _copyia
    bcrsc zeroFlag statusReg
    jump fin
    comout
    incr index
    jump loop
:fin
    halt
    

// Indirect copy : COPYIA - DGR2A compatible
%data _copyia 6
%data cpy_from 0
return 

// data zone
%data index 0
%data hw 72 101 108 108 111 44 32 119 111 114 108 100 33 0