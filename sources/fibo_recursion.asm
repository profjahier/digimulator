%define status_reg 252
%define zero_bit   0
%define carry_bit  1

// Initialise the stack head
copylr stack stack_ptr

// computes F6
copylr 6 R0
copylr r0 f_from
call f_push
call f_fibo
copyar R0   // R0 = fibo(6)
halt

// fibo(6)
// computes Fn
// To call : Push the value of n to the stack and call
// Returns : The value of Fn in the Accumulator
:f_fibo
    copylr R0 f_to
    call f_pop
    copyla 2
    subra R0
    bcrss carry_bit status_reg
    jump f_fibo_ret_num        // If it is less than 2 return it
    decr R0                    // Evaluate Fn-1
    copylr R0 f_from
    call f_push                // R0 is pushed twice, once to save
    call f_push                // it and once to stand as a param to
    call f_fibo                // the function call.
    copyar T1
    copylr R0 f_to             // Upon return from the n-1 evaluation
    call f_pop                 // step, pop R0 to restore the value it
    decr R0                    // had while, trying to evaluate the n
    copylr T1 f_from           //term.
    call f_push                // Notice here: Saving T1.
    copylr R0 f_from
    call f_push
    call f_fibo                // Now evaluate n-2
    copylr T1 f_to
    call f_pop
    addra T1                   // At this point we have the two terms
    return                     // and simply ad them
    
:f_fibo_ret_num
    copyra R0
    return

// pushes the value of whatever f_from points to, to
// the top of the stack.
:f_push
    copyrr stack_ptr f_to
    call f_copy_ind
    incr stack_ptr
    return
    
// pops the value of the top of the stack to whatever f_to
// points to.
// Note here : We re-use the value of the Accumulator which
// we may be already using in another part of the program
:f_pop
    copyar T0  // Save the Accumulator
    copyra stack_ptr
    subla stack
    bcrss zero_bit status_reg  // Note this check :
    decr stack_ptr             // it prevents >>UNDERFLOW<<
    copyra T0
    copyrr stack_ptr f_from
    call f_copy_ind
    return
    
// Memory copy by indirect addressing via self modification.
// We construct a suitable absolute
// adressing copy instruction (copyrr) and
// execute it as a sub-routine over f_from, f_to
%data f_copy_ind 7
%data f_from 0
%data f_to 0
return

%data R0 0xF0
%data T0 0xFF
%data T1 0xFF
%data stack_ptr 0
%data stack 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0 1 0x0f