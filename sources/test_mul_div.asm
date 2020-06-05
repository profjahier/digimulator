// Counts from 123
// Converts the number to str
// Outputs the counter on the serial port

%define code  0
%define data  0x80
%define cr    13
%define lf    10

initsp
copylr  12 n                //  starting number
mul     n ten
incr    n
incr    n
incr    n

:loop
    copyrr  n arg
    call    decimal
    call    newline
    incr    n
    jump    loop

:decimal
    div     arg ten         // convert binary to ASCII decimal
    copyar  buf+2
    div     arg ten
    copyar  buf+1
    div     arg ten
    copyar  buf
    copyra  buf             // output digits in reverse order
    addla   48
    comout
    copyra  buf
    copyra  buf+1
    addla   48
    comout
    copyra  buf+2
    addla   48
    comout
    return

:newline
    copyla  cr
    comout
    copyla  lf
    comout
    return

%data n 0
%data arg 0
%data buf 0 0 0
%data ten 10