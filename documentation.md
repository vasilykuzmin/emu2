## ALU
Takes 2 b-sized registers A and B and 7 bits of microcode. Returns result of operation and flag register.
Microcode:
[0] - NOT A
[1] - INC A
[2] - NOT B
[3] - INC B
[4-6] - one of operations:
000 - A
001 - B
010 - ADD
011 - BSL
100 - BSR
101 - AND
110 - OR
111 - XOR
Flag register:
[0] - Carry
[1] - Zero
[2] - NonZero
