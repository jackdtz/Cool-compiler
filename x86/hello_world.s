

.data

    hello_world: .asciz "hello world!"

    IO_protoObj:
        .word    2
        .word    1
        .word    IO_dispatch_table



    class_objTab:
        .word   IO_protObj
        .word   IO_init
        .word   Main_protObj
        .word   Main_init

    IO_dispTab:
        .word   _print_string



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




    