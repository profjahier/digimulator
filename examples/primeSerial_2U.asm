// PrimeSerial
// Olivier Lecluse
// Platform : Digirule 2B or 2U

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
    jump the_end // End on game : nb > 255
    incr nb
    jump primeloop
:isprime
    copyrr nb dataLED_reg
    // output result to serial
    call int2str
    copyra ascii_str
    comout
    copyra ascii_str+1
    comout
    copyra ascii_str+2
    comout
    copyla ' '
    comout
    // searching next prime 
    incr pi
    jump pl1
:the_end
    halt

// Test if nb is prime
:prime_test
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

// Transforms an integer to an ASCII representation
// Input:
//    nb: int
//    ascii_str: Address of the first byte of the string
// Note:
//    The Digirule2 does not understand the string data type. In this
//    example, a "string" is just three sequential bytes in memory,
//    starting at the memory address indicated by register r1.
//
// Save the arguments because they will be required later
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
%data r0 0
%data nb 0
%data dv 0
%data t0 0
%data ascii_str "000"