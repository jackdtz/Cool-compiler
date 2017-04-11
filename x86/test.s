obj_size = 8

.data
    hello_world: .asciz "hello world!"

.text
    .globl _main


_main:

    pushq %rbp
    movq %rsp, %rbp
    leaq hello_world(%rip), %rdi
    callq _print_string

    subq $obj_size, %rsp
    movq $1, %rax
    movq %rax, obj_size(%rsp)

    addq $obj_size, %rsp

    leave
    ret