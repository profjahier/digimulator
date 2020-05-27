// int2bcd: Converts a byte to BCD
// Adapted from Athanasios Anastasio's int2str program
// https://dgtools.readthedocs.io/en/latest/int2str.html

// Uses the Digirule 2B instruction Set

%define status_reg 252
%define ZFlag      0
%define Carry      1

%define ascii_str  248
%define r0         251

// Initialisation
    INITSP
    COPYLR 0 ascii_str
    COPYLR 0 249
    COPYLR 0 250

// number to convert into r0
    COPYLR 178 r0

// Test the ascii to BCD
    COPYLR ascii_str r1
    CALL int2bcd

// Test div Acc / r0
//    COPYLR 7 r0
//    COPYLA 28
//    CALL div
//    COPYRA r1 

    HALT

:int2bcd
// Transforms an integer to a BCD representation
// Input:
//    r0: int
//    r1: Address of the Most Significant Digit of result
//
// Save the arguments
    PUSHR r0
    COPYRR r1 t1
    // Divide by 100
    COPYRA r0
    COPYLR 100 r0
    CALL div
// Adjust the BCD rep and copy to the next available string position
    CALL int2bcd_adjust_and_copy
// Load the remainder, divide by 10 
    COPYRA r0
    COPYLR 10 r0
    CALL div
    CALL int2bcd_adjust_and_copy
// Load the remainder
// Notice here, the remainder is in r0 but it does not 
// go through the division. For this reason, it is simply
// copied across from number to r1 to be able to re_use the 
// adjust_and_copy procedure as is.
    COPYRR r0 r1
    CALL int2bcd_adjust_and_copy
    POPR r0
    RETURN

:int2bcd_adjust_and_copy
// puts the result to the next available string position
    COPYRI r1 t1
    INCR t1
    RETURN


// Division
:div
// Performs Acc/r0
// Returns r1:Ratio, r0:Remainder
    CBR ZFlag status_reg // Zero bit
    CBR Carry status_reg // Carry bit
    COPYLR 0 r1
:sub_again
    INCR r1
    SUBRA r0
:check_carry
// Maybe the last SUB overshot zero
    BCRSS 1 status_reg
    JUMP sub_again
// Adjust results
    ADDRA r0
    DECR r1
    COPYAR r0
    RETURN

// General Registers
%data r1 0
%data t1 0
