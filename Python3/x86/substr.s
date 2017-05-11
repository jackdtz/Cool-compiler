.data

    .globl Main_init
    .globl Main_protoObj
    .globl String_protoObj
    .globl Main_main



string_content1:
    .asciz    "enter a string\n"
    .align    8
string_content0:
    .asciz    ""
    .align    8
int_content2:    .int    5
int_content0:    .int    0
int_content1:    .int    18



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

IO_dispatch_table:
    .quad    Object_abort
    .quad    Object_copy
    .quad    IO_out_string
    .quad    IO_out_int
    .quad    IO_in_string
    .quad    _IO_in_int

Main_dispatch_table:
    .quad    Object_abort
    .quad    Object_copy
    .quad    IO_out_string
    .quad    IO_out_int
    .quad    IO_in_string
    .quad    _IO_in_int
    .quad    Main_main

Bool_dispatch_table:
    .quad    Object_abort
    .quad    Object_copy

Int_dispatch_table:
    .quad    Object_abort
    .quad    Object_copy

String_dispatch_table:
    .quad    Object_abort
    .quad    Object_copy
    .quad    String_length
    .quad    String_concat
    .quad    String_substr

Object_dispatch_table:
    .quad    Object_abort
    .quad    Object_copy
int_const2:
    .quad    3
    .quad    4
    .quad    Int_dispatch_table
    .quad    int_content2

int_const1:
    .quad    3
    .quad    4
    .quad    Int_dispatch_table
    .quad    int_content1

int_const0:
    .quad    3
    .quad    4
    .quad    Int_dispatch_table
    .quad    int_content0

string_const0:
    .quad    2
    .quad    6
    .quad    String_dispatch_table
    .quad    int_const0
    .quad    string_content0
    .align    8

string_const1:
    .quad    2
    .quad    6
    .quad    String_dispatch_table
    .quad    int_const1
    .quad    string_content1
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
    leaq int_const0(%rip), %rax
    movq -40(%rbp), %rdi
    movq %rax, 24(%rdi)

    leaq string_const0(%rip), %rax
    movq -40(%rbp), %rdi
    movq %rax, 32(%rdi)
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



Main_main:
    pushq %rbp
    movq %rsp, %rbp
    pushq %rbx
    pushq %r12
    pushq %r13
    pushq %r14
    subq $16, %rsp
    movq %rdi, -40(%rbp)
    movq -40(%rbp), %rax
    push %rdi
    subq $8, %rsp
    movq %rax, %rdi
    push %rdi
    subq $8, %rsp
    leaq string_const1(%rip), %rax
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
    movq -40(%rbp), %rdi
    movq %rax, 24(%rdi)

    movq -40(%rbp), %rax
    push %rdi
    subq $8, %rsp
    movq %rax, %rdi
    push %rdi
    subq $8, %rsp
    movq -40(%rbp), %rax
    movq 24(%rax), %rax
    push %rdi
    subq $8, %rsp
    movq %rax, %rdi
    push %rdi
    subq $8, %rsp
    leaq int_const2(%rip), %rax
    movq %rax, %rdx
    leaq int_const0(%rip), %rax
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
    leaq string_const0(%rip), %rax
    movq -40(%rbp), %rdi
    movq %rax, 24(%rdi)
    addq $16, %rsp
    popq %r14
    popq %r13
    popq %r12
    popq %rbx
    leave
    ret


