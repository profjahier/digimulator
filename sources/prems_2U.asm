// 
// displays prime numbers from 5 to 255
// uses DIV instruction - only for 2B and 2U firmwares


%define status_reg  252
%define dataLED_reg 255
%define pi          248

%define ZFlag       0
%define PFlag       3
%define Carry       1

initsp
speed 0

// prime numbers 
copylr 2 pi // 2 and 3 are primes and not computed
copylr 5 nb // start of prime search
:primeloop
    call prime_test
    bcrsc PFlag status_reg
    jump isprime
:pl1
    cbr ZFlag status_reg
    incr nb 
    bcrsc ZFlag status_reg
    jump the_end // End of game : nb > 255
    incr nb
    jump primeloop
:isprime
    copyrr nb dataLED_reg
    incr pi
    jump pl1
:the_end
    halt


:prime_test
// Tests if nb is prime
    copyrr nb dv
:loopdiv
    decr dv
    decr dv
    copyrr nb r0 // arg1 is modified by div, 
    div r0 dv    // arg1 is the quotient, acc the remainder
    addla 0
    bcrsc ZFlag status_reg 
    jump not_prime
    copyra dv
    subla 3
    bcrss ZFlag status_reg
    jump loopdiv
// Number is prime
    sbr PFlag status_reg
    return
:not_prime
    cbr PFlag status_reg
    return    

// General Registers
%data r0 0
%data nb 0
%data dv 0