

.data

    hello_world: .asciz "hello world!"


    classTab:
        .word 0

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




    