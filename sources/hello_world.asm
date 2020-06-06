%define statusReg 0b11111100
%define zeroFlag  0

speed 128
initsp
:start 
    copylr hw loop+1
    :loop
        copyra  0    // loop+1 is the argument of copyra
        incr loop+1  // this program modifies itself
        addla 0      // in order to do the indirect adressing
        bcrsc zeroFlag statusReg
        jump start
        comout
        jump loop

// data zone
%data hw "Hello, World!" 0