@macro PUSH stack reg
SET *stack reg
ADD stack 1
@endmacro

@macro POP stack reg
SUB stack 1
SET reg *stack
@endmacro

# static call
@macro CALL stack tag
SET *stack ret
ADD stack 1
JMP tag
ret!:
@endmacro

# static ret
@macro RET stack
SUB stack 1
JMP *stack
@endmacro


SET R3 1000
loop:
CALL R3 main
JMP loop
STOP

@macro print col
SET R4 col
OR R4 0b1000000000000000
XOR R4 R4
@endmacro

main:

print 0
print 0b111110000000000
print 0b000001111100000
print 0b000000000011111
SET R5 0b111111111111111
print R5

RET R3
