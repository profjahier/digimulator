// div and int2str functions from 
// https://dgtools.readthedocs.io/en/latest/int2str.htm

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
    copyrr nb r0
    copylr ascii_str r1
    call int2str
    copyra ascii_str
    comout
    copyra ascii_str1
    comout
    copyra ascii_str2
    comout
    copyla 32
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
    copyrr dv r0
    copyra nb
    call div
    copyra r0 
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
    
// Division
:div
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
    decr r1
    copyar r0
    return

// Transforms an integer to an ASCII representation
// Input:
//    r0: int
//    r1: Address of the first byte of the string
// Note:
//    The Digirule2 does not understand the string data type. In this
//    example, a "string" is just three sequential bytes in memory,
//    starting at the memory address indicated by register r1.
//
// Save the arguments because they will be required later
:int2str
    COPYRR nb t0
    COPYRR r1 t1
    // Divide by 100
    COPYRA r0
    COPYLR 100 r0
    CALL div
    // Adjust the ascii rep and copy to the next available string position
    CALL int2str_adjust_and_copy
    // Load the remainder, divide by 10
    COPYRA r0
    COPYLR 10 r0
    CALL div
    CALL int2str_adjust_and_copy
    // Load the remainder
    // Notice here, the remainder is in r0 but it does not
    // go through the division. For this reason, it is simply
    // copied across from r0 to r1 to be able to re_use the
    // adjust_and_copy procedure as is.
    COPYRR r0 r1
    CALL int2str_adjust_and_copy
    RETURN
:int2str_adjust_and_copy
    // Adds the ascii 0 value (48) to the order of mag multiplier
    // and puts the result to the next available string position
    COPYRA r1
    ADDLA 48
    COPYAR t2
    COPYLR t2 cpy_from
    COPYRR t1 cpy_to
    CALL cpy_ind
    INCR t1
    RETURN



// Indirect copy - DGR2A compatible
// Athanasios Anastasiou
%data cpy_ind 7
%data cpy_from 0
%data cpy_to 0 
return 

// General Registers
%data r0 0
%data r1 0
%data nb 0
%data dv 0
%data t0 0
%data t1 0
%data t2 0
%data ascii_str 0
%data ascii_str1 0
%data ascii_str2 0 