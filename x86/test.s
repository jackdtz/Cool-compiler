


.data

.text

    .globl _main


_main:
    push %rbp
    movq %rsp, %rbp

    push %r8
    push %r9
    push %r10
    push %r11

    subq $16, %rsp

    movq $1, -40(%rbp)

    movq -40(%rbp), %rax

    popq %r11
    popq %r10
    popq %r9
    popq %r8

    leave
    ret
