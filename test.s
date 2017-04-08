.data

IO_protoObj:
    .word    2
    .word    1
    .word    IO_dispatch_table

Object_protoObj:
    .word    1
    .word    1
    .word    Object_dispatch_table

Bool_protoObj:
    .word    5
    .word    2
    .word    Bool_dispatch_table
    .word    0

String_protoObj:
    .word    3
    .word    3
    .word    String_dispatch_table
    .word    0
    .word    0

Int_protoObj:
    .word    4
    .word    2
    .word    Int_dispatch_table
    .word    0

hello_world: .asciz "hello world!"

.text

    .globl _print_string
    .globl _main

_main:

    pushq %rbp
    movq %rsp, %rbp
    leaq hello_world(%rip), %rdi
    callq _print_string

    movq %rbp, %rsp
    popq %rbp