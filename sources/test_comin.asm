// Tests a non blocking way of reading of the serial port
// Press ESC to end the demo

%define dataLED   255
%define adrLED    254
%define statusReg 252
%define ZFlag     0
%define hideadr   2

initsp
speed 2
copylr 0 dataLED
sbr hideadr statusReg

:loop
    comrdy
    bcrss ZFlag statusReg
    jump read
    incr dataLED
    jump loop
:read
    comin
    copyar adrLED
    subla 27
    bcrss ZFlag statusReg
    jump loop   
    halt 