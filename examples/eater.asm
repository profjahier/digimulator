// 
// Converts a 2-bytes integer into a string 
// Print the string over serial 
// This is following Ben Easter's algorithm 
// described here : https://youtu.be/v3-a-zqKfgA 
// Adaptation to Digirule by Olivier Lecluse 
// 
%define _sr 252 
%define _dr 255 
%define _ar 254 
%define _sar 2 
%define _c 1 
%define _z 0

initsp	
speed	0 

sbr	_sar _sr 
// Initialize value to be the number to convert 
copyrr	number value 
copyrr	number+1 value+1 
// Initialize the stack pointer 
copylr	stack stackPtr 

:divide 
// Initialize the remainder to 0 
  copylr	0 mod10 
  copylr	0 mod10+1 
  sbr	_c _sr // XX Carry is inverted later 

  copylr	16 idx 
:divloop 
// Rotate quotient and remainder 
// Carry is taken into account for shifting 
// We have to invert it // XX 
  call	invert_carry 

  copyrr	value _dr 
  copyrr	value+1 _ar 
  shiftrl	value 
  shiftrl	value+1 
  shiftrl	mod10 
  shiftrl	mod10+1 

// Acc, tmp = dividend - divisor 
// Here, carry is borrow 
  cbr	_c _sr // XX 
  copyra	mod10 
  subla	10 
  copyar	tmp 
  copyra	mod10+1 
  subla	0 

  bcrsc	_c _sr // XX 
  jump	ignore_result // branch if dividend < divisor 
  copyrr	tmp mod10 
  copyar	mod10+1 
:ignore_result 
  decrjz	idx 
  jump	divloop 
// Carry is taken into account for shifting 
// We have to invert it // XX 
  call	invert_carry 
  shiftrl	value // shift in the last bit of the quotient 
  shiftrl	value+1 

  copyra	mod10 
// cbr _c, _sr // XX 
// push the remainder into the stack 
  copyai	stackPtr 
  incr	stackPtr 

// if value != 0, then continue dividing 
  copyra	value 
  orra	value+1 
  bcrss	_z _sr 
  jump	divide // branch if value is not zero 

  call	stack_out 
  halt	
  jump	0 

:invert_carry 
// ACC is lost in this operation 
  copyra	_sr // XX 
  xorla	2 // XX 
  copyar	_sr // XX 
  return	

:stack_out 
// pops out the stack into serial 
  decr	stackPtr 
  copyia	stackPtr 
  orla	'0' 
  comout	
// test if we reached the head of the stack 
  copyra	stackPtr 
  xorla	stack 
  bcrss	_z _sr 
  jump	stack_out 
  return	


%data value 0 0 // 2 bytes 
%data mod10 0 0 // 2 bytes 
%data number 0xc1 0x06 // 1729 little indian 
%data tmp 0 // temp register 
%data idx 0 
%data stack 0 0 0 0 0 0 
%data stackPtr 0 
