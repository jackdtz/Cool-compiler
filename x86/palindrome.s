.data

    .globl Main_init
    .globl Main_protoObj
    .globl String_protoObj
    .globl Main_main


class_objTab:
    .quad    Object_protoObj
    .quad    Object_init
    .quad    IO_protoObj
    .quad    IO_init
    .quad    String_protoObj
    .quad    String_init
    .quad    Int_protoObj
    .quad    Int_init
    .quad    Bool_protoObj
    .quad    Bool_init
    .quad    Main_protoObj
    .quad    Main_init

Object_protoObj:
    .quad    0
    .quad    3
    .quad    Object_dispatch_table

IO_protoObj:
    .quad    1
    .quad    3
    .quad    IO_dispatch_table

String_protoObj:
    .quad    2
    .quad    5
    .quad    String_dispatch_table
    .quad    0
    .quad    0

Int_protoObj:
    .quad    3
    .quad    4
    .quad    Int_dispatch_table
    .quad    0

Bool_protoObj:
    .quad    4
    .quad    4
    .quad    Bool_dispatch_table
    .quad    0

Main_protoObj:
    .quad    5
    .quad    4
    .quad    Main_dispatch_table
    .quad    0

String_dispatch_table:
    .quad    Object_abort
    .quad    Object_copy
    .quad    String_length
    .quad    String_concat
    .quad    String_substr

IO_dispatch_table:
    .quad    Object_abort
    .quad    Object_copy
    .quad    IO_out_string
    .quad    IO_out_int
    .quad    IO_in_string
    .quad    _IO_in_int

Bool_dispatch_table:
    .quad    Object_abort
    .quad    Object_copy

Main_dispatch_table:
    .quad    Object_abort
    .quad    Object_copy
    .quad    IO_out_string
    .quad    IO_out_int
    .quad    IO_in_string
    .quad    _IO_in_int
    .quad    Main_pal
    .quad    Main_main

Object_dispatch_table:
    .quad    Object_abort
    .quad    Object_copy

Int_dispatch_table:
    .quad    Object_abort
    .quad    Object_copy
int_const0:
    .quad    3
    .quad    4
    .quad    Int_dispatch_table
    .quad    0

int_const2:
    .quad    3
    .quad    4
    .quad    Int_dispatch_table
    .quad    2

int_const4:
    .quad    3
    .quad    4
    .quad    Int_dispatch_table
    .quad    25

int_const1:
    .quad    3
    .quad    4
    .quad    Int_dispatch_table
    .quad    1

int_const5:
    .quad    3
    .quad    4
    .quad    Int_dispatch_table
    .quad    29

int_const3:
    .quad    3
    .quad    4
    .quad    Int_dispatch_table
    .quad    18

string_const0:
    .quad    2
    .quad    6
    .quad    String_dispatch_table
    .quad    int_const0
    .asciz    ""
    .align    8

string_const3:
    .quad    2
    .quad    6
    .quad    String_dispatch_table
    .quad    int_const3
    .asciz    "enter a string\n"
    .align    8

string_const5:
    .quad    2
    .quad    6
    .quad    String_dispatch_table
    .quad    int_const5
    .asciz    "that was not a palindrome\n"
    .align    8

string_const4:
    .quad    2
    .quad    6
    .quad    String_dispatch_table
    .quad    int_const4
    .asciz    "that was a palindrome\n"
    .align    8


.text



Object_init:
    pushq %rbp
    movq %rsp, %rbp
    pushq %rbx
    pushq %r12
    pushq %r13
    pushq %r14
    popq %r14
    popq %r13
    popq %r12
    popq %rbx
    leave
    ret






IO_init:
    pushq %rbp
    movq %rsp, %rbp
    pushq %rbx
    pushq %r12
    pushq %r13
    pushq %r14
    pushq %rdx
    pushq %rcx
    pushq %rsi
    pushq %rdi
    pushq %r8
    pushq %r9
    pushq %r10
    subq $8, %rsp
    callq Object_init
    addq $8, %rsp
    popq %r10
    popq %r9
    popq %r8
    popq %rdi
    popq %rsi
    popq %rcx
    popq %rdx
    popq %r14
    popq %r13
    popq %r12
    popq %rbx
    leave
    ret





String_init:
    pushq %rbp
    movq %rsp, %rbp
    pushq %rbx
    pushq %r12
    pushq %r13
    pushq %r14
    pushq %rdx
    pushq %rcx
    pushq %rsi
    pushq %rdi
    pushq %r8
    pushq %r9
    pushq %r10
    subq $8, %rsp
    callq Object_init
    addq $8, %rsp
    popq %r10
    popq %r9
    popq %r8
    popq %rdi
    popq %rsi
    popq %rcx
    popq %rdx
    subq $16, %rsp
    movq %rdi, -40(%rbp)
    leaq string_const0(%rip), %rax
    addq $32, %rax
    movq -40(%rbp), %rdi
    movq %rax, 32(%rdi)

    leaq int_const0(%rip), %rax
    movq 24(%rax), %rax
    movq -40(%rbp), %rdi
    movq %rax, 24(%rdi)
    addq $16, %rsp
    popq %r14
    popq %r13
    popq %r12
    popq %rbx
    leave
    ret


Int_init:
    pushq %rbp
    movq %rsp, %rbp
    pushq %rbx
    pushq %r12
    pushq %r13
    pushq %r14
    pushq %rdx
    pushq %rcx
    pushq %rsi
    pushq %rdi
    pushq %r8
    pushq %r9
    pushq %r10
    subq $8, %rsp
    callq Object_init
    addq $8, %rsp
    popq %r10
    popq %r9
    popq %r8
    popq %rdi
    popq %rsi
    popq %rcx
    popq %rdx
    subq $16, %rsp
    movq %rdi, -40(%rbp)
    leaq int_const0(%rip), %rax
    movq 24(%rax), %rax
    movq -40(%rbp), %rdi
    movq %rax, 24(%rdi)
    addq $16, %rsp
    popq %r14
    popq %r13
    popq %r12
    popq %rbx
    leave
    ret


Bool_init:
    pushq %rbp
    movq %rsp, %rbp
    pushq %rbx
    pushq %r12
    pushq %r13
    pushq %r14
    pushq %rdx
    pushq %rcx
    pushq %rsi
    pushq %rdi
    pushq %r8
    pushq %r9
    pushq %r10
    subq $8, %rsp
    callq Object_init
    addq $8, %rsp
    popq %r10
    popq %r9
    popq %r8
    popq %rdi
    popq %rsi
    popq %rcx
    popq %rdx
    subq $16, %rsp
    movq %rdi, -40(%rbp)
    movq $0, %rax
    movq -40(%rbp), %rdi
    movq %rax, 24(%rdi)
    addq $16, %rsp
    popq %r14
    popq %r13
    popq %r12
    popq %rbx
    leave
    ret



Main_pal:
    pushq %rbp
    movq %rsp, %rbp
    pushq %rbx
    pushq %r12
    pushq %r13
    pushq %r14
    subq $16, %rsp
    movq %rdi, -40(%rbp)
    movq %rsi, -48(%rbp)
    movq -48(%rbp), %rax
    push %rdi
    subq $8, %rsp
    movq %rax, %rdi
    push %rdi
    subq $8, %rsp
    addq $8, %rsp
    popq %rdi
    movq 16(%rdi), %r10
    movq 16(%r10), %r10
    pushq %rdx
    pushq %rcx
    pushq %rsi
    pushq %rdi
    pushq %r8
    pushq %r9
    pushq %r10
    subq $8, %rsp
    callq *%r10
    addq $8, %rsp
    popq %r10
    popq %r9
    popq %r8
    popq %rdi
    popq %rsi
    popq %rcx
    popq %rdx
    addq $8, %rsp
    popq %rdi
    pushq %rax
    leaq int_const0(%rip), %rax
    movq 24(%rax), %rax
    popq %rdi
    cmpq %rax, %rdi
    sete %al
    movzbq %al, %rax
    cmpq $1, %rax
    jne Main.pal.else.0
    movq $1, %rax

    jmp Main.pal.end.0

Main.pal.else.0:
    movq -48(%rbp), %rax
    push %rdi
    subq $8, %rsp
    movq %rax, %rdi
    push %rdi
    subq $8, %rsp
    addq $8, %rsp
    popq %rdi
    movq 16(%rdi), %r10
    movq 16(%r10), %r10
    pushq %rdx
    pushq %rcx
    pushq %rsi
    pushq %rdi
    pushq %r8
    pushq %r9
    pushq %r10
    subq $8, %rsp
    callq *%r10
    addq $8, %rsp
    popq %r10
    popq %r9
    popq %r8
    popq %rdi
    popq %rsi
    popq %rcx
    popq %rdx
    addq $8, %rsp
    popq %rdi
    pushq %rax
    leaq int_const1(%rip), %rax
    movq 24(%rax), %rax
    popq %rdi
    cmpq %rax, %rdi
    sete %al
    movzbq %al, %rax
    cmpq $1, %rax
    jne Main.pal.else.1
    movq $1, %rax

    jmp Main.pal.end.1

Main.pal.else.1:
    movq -48(%rbp), %rax
    push %rdi
    subq $8, %rsp
    movq %rax, %rdi
    push %rdi
    subq $8, %rsp
    leaq int_const1(%rip), %rax
    movq 24(%rax), %rax
    movq %rax, %rdx
    leaq int_const0(%rip), %rax
    movq 24(%rax), %rax
    movq %rax, %rsi
    addq $8, %rsp
    popq %rdi
    movq 16(%rdi), %r10
    movq 32(%r10), %r10
    pushq %rdx
    pushq %rcx
    pushq %rsi
    pushq %rdi
    pushq %r8
    pushq %r9
    pushq %r10
    subq $8, %rsp
    callq *%r10
    addq $8, %rsp
    popq %r10
    popq %r9
    popq %r8
    popq %rdi
    popq %rsi
    popq %rcx
    popq %rdx
    addq $8, %rsp
    popq %rdi
    pushq %rax
    movq -48(%rbp), %rax
    push %rdi
    subq $8, %rsp
    movq %rax, %rdi
    push %rdi
    subq $8, %rsp
    leaq int_const1(%rip), %rax
    movq 24(%rax), %rax
    movq %rax, %rdx
    movq -48(%rbp), %rax
    push %rdi
    subq $8, %rsp
    movq %rax, %rdi
    push %rdi
    subq $8, %rsp
    addq $8, %rsp
    popq %rdi
    movq 16(%rdi), %r10
    movq 16(%r10), %r10
    pushq %rdx
    pushq %rcx
    pushq %rsi
    pushq %rdi
    pushq %r8
    pushq %r9
    pushq %r10
    subq $8, %rsp
    callq *%r10
    addq $8, %rsp
    popq %r10
    popq %r9
    popq %r8
    popq %rdi
    popq %rsi
    popq %rcx
    popq %rdx
    addq $8, %rsp
    popq %rdi

    push %rax
    leaq int_const1(%rip), %rax
    movq 24(%rax), %rax

    movq %rax, %rdi
    popq %rax
    subq %rdi, %rax
    movq %rax, %rsi
    addq $8, %rsp
    popq %rdi
    movq 16(%rdi), %r10
    movq 32(%r10), %r10
    pushq %rdx
    pushq %rcx
    pushq %rsi
    pushq %rdi
    pushq %r8
    pushq %r9
    pushq %r10
    subq $8, %rsp
    callq *%r10
    addq $8, %rsp
    popq %r10
    popq %r9
    popq %r8
    popq %rdi
    popq %rsi
    popq %rcx
    popq %rdx
    addq $8, %rsp
    popq %rdi
    popq %rdi
    cmpq %rax, %rdi
    sete %al
    movzbq %al, %rax
    cmpq $1, %rax
    jne Main.pal.else.2
    movq -40(%rbp), %rax
    push %rdi
    subq $8, %rsp
    movq %rax, %rdi
    push %rdi
    subq $8, %rsp
    movq -48(%rbp), %rax
    push %rdi
    subq $8, %rsp
    movq %rax, %rdi
    push %rdi
    subq $8, %rsp
    movq -48(%rbp), %rax
    push %rdi
    subq $8, %rsp
    movq %rax, %rdi
    push %rdi
    subq $8, %rsp
    addq $8, %rsp
    popq %rdi
    movq 16(%rdi), %r10
    movq 16(%r10), %r10
    pushq %rdx
    pushq %rcx
    pushq %rsi
    pushq %rdi
    pushq %r8
    pushq %r9
    pushq %r10
    subq $8, %rsp
    callq *%r10
    addq $8, %rsp
    popq %r10
    popq %r9
    popq %r8
    popq %rdi
    popq %rsi
    popq %rcx
    popq %rdx
    addq $8, %rsp
    popq %rdi

    push %rax
    leaq int_const2(%rip), %rax
    movq 24(%rax), %rax

    movq %rax, %rdi
    popq %rax
    subq %rdi, %rax
    movq %rax, %rdx
    leaq int_const1(%rip), %rax
    movq 24(%rax), %rax
    movq %rax, %rsi
    addq $8, %rsp
    popq %rdi
    movq 16(%rdi), %r10
    movq 32(%r10), %r10
    pushq %rdx
    pushq %rcx
    pushq %rsi
    pushq %rdi
    pushq %r8
    pushq %r9
    pushq %r10
    subq $8, %rsp
    callq *%r10
    addq $8, %rsp
    popq %r10
    popq %r9
    popq %r8
    popq %rdi
    popq %rsi
    popq %rcx
    popq %rdx
    addq $8, %rsp
    popq %rdi
    movq %rax, %rsi
    addq $8, %rsp
    popq %rdi
    movq 16(%rdi), %r10
    movq 48(%r10), %r10
    pushq %rdx
    pushq %rcx
    pushq %rsi
    pushq %rdi
    pushq %r8
    pushq %r9
    pushq %r10
    subq $8, %rsp
    callq *%r10
    addq $8, %rsp
    popq %r10
    popq %r9
    popq %r8
    popq %rdi
    popq %rsi
    popq %rcx
    popq %rdx
    addq $8, %rsp
    popq %rdi

    jmp Main.pal.end.2

Main.pal.else.2:
    movq $0, %rax

Main.pal.end.2:

Main.pal.end.1:

Main.pal.end.0:
    addq $16, %rsp
    popq %r14
    popq %r13
    popq %r12
    popq %rbx
    leave
    ret


Main_main:
    pushq %rbp
    movq %rsp, %rbp
    pushq %rbx
    pushq %r12
    pushq %r13
    pushq %r14
    subq $16, %rsp
    movq %rdi, -40(%rbp)
    leaq int_const1(%rip), %rax
    movq 24(%rax), %rax
    negq %rax
    movq -40(%rbp), %rdi
    movq %rax, 24(%rdi)

    movq -40(%rbp), %rax
    push %rdi
    subq $8, %rsp
    movq %rax, %rdi
    push %rdi
    subq $8, %rsp
    leaq string_const3(%rip), %rax
    addq $32, %rax
    movq %rax, %rsi
    addq $8, %rsp
    popq %rdi
    movq 16(%rdi), %r10
    movq 16(%r10), %r10
    pushq %rdx
    pushq %rcx
    pushq %rsi
    pushq %rdi
    pushq %r8
    pushq %r9
    pushq %r10
    subq $8, %rsp
    callq *%r10
    addq $8, %rsp
    popq %r10
    popq %r9
    popq %r8
    popq %rdi
    popq %rsi
    popq %rcx
    popq %rdx
    addq $8, %rsp
    popq %rdi

    movq -40(%rbp), %rax
    push %rdi
    subq $8, %rsp
    movq %rax, %rdi
    push %rdi
    subq $8, %rsp
    movq -40(%rbp), %rax
    push %rdi
    subq $8, %rsp
    movq %rax, %rdi
    push %rdi
    subq $8, %rsp
    addq $8, %rsp
    popq %rdi
    movq 16(%rdi), %r10
    movq 32(%r10), %r10
    pushq %rdx
    pushq %rcx
    pushq %rsi
    pushq %rdi
    pushq %r8
    pushq %r9
    pushq %r10
    subq $8, %rsp
    callq *%r10
    addq $8, %rsp
    popq %r10
    popq %r9
    popq %r8
    popq %rdi
    popq %rsi
    popq %rcx
    popq %rdx
    addq $8, %rsp
    popq %rdi
    movq %rax, %rsi
    addq $8, %rsp
    popq %rdi
    movq 16(%rdi), %r10
    movq 48(%r10), %r10
    pushq %rdx
    pushq %rcx
    pushq %rsi
    pushq %rdi
    pushq %r8
    pushq %r9
    pushq %r10
    subq $8, %rsp
    callq *%r10
    addq $8, %rsp
    popq %r10
    popq %r9
    popq %r8
    popq %rdi
    popq %rsi
    popq %rcx
    popq %rdx
    addq $8, %rsp
    popq %rdi
    cmpq $1, %rax
    jne Main.main.else.3
    movq -40(%rbp), %rax
    push %rdi
    subq $8, %rsp
    movq %rax, %rdi
    push %rdi
    subq $8, %rsp
    leaq string_const4(%rip), %rax
    addq $32, %rax
    movq %rax, %rsi
    addq $8, %rsp
    popq %rdi
    movq 16(%rdi), %r10
    movq 16(%r10), %r10
    pushq %rdx
    pushq %rcx
    pushq %rsi
    pushq %rdi
    pushq %r8
    pushq %r9
    pushq %r10
    subq $8, %rsp
    callq *%r10
    addq $8, %rsp
    popq %r10
    popq %r9
    popq %r8
    popq %rdi
    popq %rsi
    popq %rcx
    popq %rdx
    addq $8, %rsp
    popq %rdi

    jmp Main.main.end.3

Main.main.else.3:
    movq -40(%rbp), %rax
    push %rdi
    subq $8, %rsp
    movq %rax, %rdi
    push %rdi
    subq $8, %rsp
    leaq string_const5(%rip), %rax
    addq $32, %rax
    movq %rax, %rsi
    addq $8, %rsp
    popq %rdi
    movq 16(%rdi), %r10
    movq 16(%r10), %r10
    pushq %rdx
    pushq %rcx
    pushq %rsi
    pushq %rdi
    pushq %r8
    pushq %r9
    pushq %r10
    subq $8, %rsp
    callq *%r10
    addq $8, %rsp
    popq %r10
    popq %r9
    popq %r8
    popq %rdi
    popq %rsi
    popq %rcx
    popq %rdx
    addq $8, %rsp
    popq %rdi

Main.main.end.3:
    addq $16, %rsp
    popq %r14
    popq %r13
    popq %r12
    popq %rbx
    leave
    ret

Main_init:
    pushq %rbp
    movq %rsp, %rbp
    pushq %rbx
    pushq %r12
    pushq %r13
    pushq %r14
    pushq %rdx
    pushq %rcx
    pushq %rsi
    pushq %rdi
    pushq %r8
    pushq %r9
    pushq %r10
    subq $8, %rsp
    callq IO_init
    addq $8, %rsp
    popq %r10
    popq %r9
    popq %r8
    popq %rdi
    popq %rsi
    popq %rcx
    popq %rdx
    subq $16, %rsp
    movq %rdi, -40(%rbp)
    leaq int_const0(%rip), %rax
    movq 24(%rax), %rax
    movq -40(%rbp), %rdi
    movq %rax, 24(%rdi)
    addq $16, %rsp
    popq %r14
    popq %r13
    popq %r12
    popq %rbx
    leave
    ret


