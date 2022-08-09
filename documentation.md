## Flag register
[0] - Carry
[1] - Zero
[2] - NonZero
[3] - Positive
[4] - Negative

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

## CPU
Lookup microcode:
[0-6] - ALU microcode
[7] - INC program counter (register 0)
[8-10] - Save ALU result in A if 000 - not save, 001 - save, flag register(register 1) [i - 2]

Operations:
OpCode| Lookup        |
00000 | 0000000 1 000 | NOP  [0, 0] - NOP

10000 | 0000001 1 001 | MOV  [A, B] - Copy B to A
01000 | 0000000 1 001 | SET  [A, N] - Set A to N (N < 2**22)


11000 | 0100001 1 001 | INC  [A, 0] - A++
00100 | 0000010 1 001 | ADD  [A, B] - A = A + B
10100 | 0011010 1 001 | SUB  [A, B] - A = A - B
01100 | 1100010 1 001 | ASUB [A, B] - A = B - A
11100 | 0011010 1 000 | NSUB [A, B] - A - B
00010 | 0000101 1 001 | AND  [A, B] - A = A AND B
10010 | 1010110 1 001 | NAND [A, B] - A = A NAND B
01010 | 0000110 1 001 | OR   [A, B] - A = A OR B
11010 | 1010101 1 001 | NOR  [A, B] - A = A NOR B
00110 | 0000111 1 001 | XOR  [A, B] - A = A XOR B
10110 | 1000111 1 001 | XNOR [A, B] - A = A XNOR B
01110 | 0000011 1 001 | BSL  [A, B] - A = A BSL B
11110 | 0000100 1 001 | BSR  [A, B] - A = A BSR B

00001 | 0000000 0 000 | STOP [0, 0] - infinite loop
10001 | 0000001 0 001 | JMP  [0, m] - program counter (register[0]) = m
01001 | 0000001 0 010 | JC   [0, m] - JMP if carry
11001 | 0000001 0 011 | JZ   [0, m] - JMP if zero
00101 | 0000001 0 100 | JNZ  [0, m] - JMP if nonzero
10101 | 0000001 0 101 | JP   [0, m] - JMP if positive
01101 | 0000001 0 110 | JN   [0, m] - JMP if negative