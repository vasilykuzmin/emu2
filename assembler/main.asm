@macro PUSH stack reg
SET *stack Rreg
ADD Rstack 1
@endmacro

@macro POP stack reg
SUB Rstack 1
SET Rreg *stack
@endmacro

# static call
@macro CALL stack tag
SET *stack ret
ADD Rstack 1
JMP tag
ret!:
@endmacro

# static ret
@macro RET stack
SUB Rstack 1
JMP *stack
@endmacro


SET R3 1000
loop:
CALL 3 main
JMP loop
STOP

@macro print reg
SET R4 Rreg
OR R4 0b1000000000000000
XOR R4 R4
@endmacro

main:

SET R5 0
print 5
SET R5 0b111110000000000
print 5
SET R5 0b000001111100000
print 5
SET R5 0b000000000011111
print 5
SET R5 0b111111111111111
print 5

RET 3
