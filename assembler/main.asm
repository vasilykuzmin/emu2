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

CALL 3 main
CALL 3 main
CALL 3 main

STOP


main:
ADD R5 1
RET 3