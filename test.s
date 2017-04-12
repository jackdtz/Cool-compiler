.data

hello_world: .asciz "hello world!"

.text

    .globl _print_string
    .globl _main

_main:

    pushq %rbp
    movq %rsp, %rbp
    leaq hello_world(%rip), %rdi
    callq _print_string

    movq $24, %rdi
    callq _malloc

    movq %rbp, %rsp
    popq %rbp