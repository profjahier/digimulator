%define statusReg 252
%define ZFlag     0

copylr 0 count
:loop
    copyra count
    comout 
    incr count
    bcrss ZFlag statusReg
    jump loop 
    halt
%data count 0