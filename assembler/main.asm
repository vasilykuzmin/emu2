@macro PUSH stack reg
SET *stack Rreg
ADD Rstack 1
@endmacro

@macro POP stack reg
SUB Rstack 1
SET Rreg *stack
@endmacro

@macro test
JMP testtag
ADD R4 1
testtag!:
ADD R5 1
@endmacro

test
test
test

STOP
