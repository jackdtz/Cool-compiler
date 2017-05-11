.data

    .globl Main_init
    .globl Main_protoObj
    .globl String_protoObj
    .globl Main_main



string_content0:
    .asciz    ""
    .align    8
string_content2:
    .asciz    "this is false\n"
    .align    8
string_content1:
    .asciz    "this is true\n"
    .align    8



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
    .quad    3
    .quad    Main_dispatch_table

Main_dispatch_table:
    .quad    Object_abort
    .quad    Object_copy
    .quad    IO_out_string
    .quad    IO_out_int
    .quad    IO_in_string
    .quad    _IO_in_int
    .quad    Main_main

Int_dispatch_table:
    .quad    Object_abort
    .quad    Object_copy

Object_dispatch_table:
    .quad    Object_abort
    .quad    Object_copy

Bool_dispatch_table:
    .quad    Object_abort
    .quad    Object_copy

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
int_const2:
    .quad    3
    .quad    4
    .quad    Int_dispatch_table
    .quad    17

int_const1:
    .quad    3
    .quad    4
    .quad    Int_dispatch_table
    .quad    16

int_const0:
    .quad    3
    .quad    4
    .quad    Int_dispatch_table
    .quad    0

string_const0:
    .quad    2
    .quad    6
    .quad    String_dispatch_table
    .quad    int_const0
    .quad    string_content0
    .align    8

string_const2:
    .quad    2
    .quad    6
    .quad    String_dispatch_table
    .quad    int_const2
    .quad    string_content2
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
    movq $0, %rax
    cmpq $1, %rax
    jne Main.main.else.0
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

    jmp Main.main.end.0

Main.main.else.0:
    movq -40(%rbp), %rax
    push %rdi
    subq $8, %rsp
    movq %rax, %rdi
    push %rdi
    subq $8, %rsp
    leaq string_const2(%rip), %rax
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

Main.main.end.0:
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
    popq %r14
    popq %r13
    popq %r12
    popq %rbx
    leave
    ret


