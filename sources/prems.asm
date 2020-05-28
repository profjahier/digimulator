%define status_reg  252
%define dataLED_reg 255
%define ZFlag       0
%define PFlag       3
%define Carry       1

initsp
speed 1

// prime numbers 
copylr 2 pi // 2 and 3 are primes and not computed
copylr 5 nb // start of prime search
:primeloop
    call prime_test
    bcrsc PFlag status_reg
    call isprime
:pl1
    cbr ZFlag status_reg
    incr nb 
    bcrsc ZFlag status_reg
    jump the_end // End on game : nb > 255
    incr nb
    jump primeloop
:isprime
    incr pi
    copyrr nb dataLED_reg
    jump pl1
:the_end
    copyrr pi dataLED_reg
    halt

:isprime
     

:prime_test
// Tests if nb is prime
    copyrr nb dv
:loopdiv
    decr dv
    decr dv
    copyrr dv r0
    copyra nb
    call modulo
    bcrsc ZFlag status_reg 
    jump not_prime
    copyra dv
    subla 3
    bcrss ZFlag status_reg
    jump loopdiv
// Number is prime
    copyrr nb dataLED_reg
    sbr PFlag status_reg
    return
:not_prime
    cbr PFlag status_reg
    return    
    
// Division
:modulo
// Performs Acc/r0
// Returns Remainder Acc % r0 into Accumulator
    cbr ZFlag status_reg // Zero bit
    cbr Carry status_reg // Carry bit
    copylr 0 r1
:sub_again
    incr r1
    subra r0
:check_carry
// Maybe the last SUB overshot zero
    bcrss 1 status_reg
    jump sub_again
// Adjust results
    addra r0
    return

// General Registers
%data r0 0
%data r1 0
%data nb 0
%data dv 0
%data pi 0
