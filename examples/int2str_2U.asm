// Converts a byte to BCD
// Uses the Digirule 2B/U instruction Set

%define status_reg 252
%define ZFlag      0
%define Carry      1

%define ascii_str  248

// Initialisation
    INITSP

// number to convert into nb
    COPYLR 108 nb

// Test the ascii to BCD
    CALL int2str

// Test div Acc / r0
//    COPYLR 7 r0
//    COPYLA 28
//    CALL div
//    COPYRA r1 

    HALT

:int2str
    COPYRR nb t0
    COPYLR 10 r0
    DIV t0 r0
    ADDLA '0'
    COPYAR ascii_str+2
    
    div t0 r0
    ADDLA '0' 
    COPYAR ascii_str+1
    
    COPYRA t0
    ADDLA '0'
    COPYAR ascii_str
    RETURN

// General Registers
%data nb 0
%data r0 0
%data t0 0
