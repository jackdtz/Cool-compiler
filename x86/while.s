.data

    .globl Main_init
    .globl Main_protoObj
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
    .quad    string_const1

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
    .quad    _IO_in_string
    .quad    _IO_in_int

Int_dispatch_table:
    .quad    Object_abort
    .quad    Object_copy

Object_dispatch_table:
    .quad    Object_abort
    .quad    Object_copy

Bool_dispatch_table:
    .quad    Object_abort
    .quad    Object_copy

Main_dispatch_table:
    .quad    Object_abort
    .quad    Object_copy
    .quad    IO_out_string
    .quad    IO_out_int
    .quad    _IO_in_string
    .quad    _IO_in_int
    .quad    Main_whileloop
    .quad    Main_main
int_const5:
    .quad    3
    .quad    4
    .quad    Int_dispatch_table
    .quad    1

int_const4:
    .quad    3
    .quad    4
    .quad    Int_dispatch_table
    .quad    2

int_const3:
    .quad    3
    .quad    4
    .quad    Int_dispatch_table
    .quad    0

int_const6:
    .quad    3
    .quad    4
    .quad    Int_dispatch_table
    .quad    10

string_const1:
    .quad    2
    .quad    6
    .quad    String_dispatch_table
    .quad    int_const3
    .asciz    ""
    .align    8

string_const4:
    .quad    2
    .quad    6
    .quad    String_dispatch_table
    .quad    int_const4
    .asciz    ""
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
    movq %rdi, %rdi
    pushq %rdx
    pushq %rcx
    pushq %rsi
    pushq %rdi
    pushq %r8
    pushq %r9
    pushq %r10
    callq Object_init
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
    movq %rdi, %rdi
    pushq %rdx
    pushq %rcx
    pushq %rsi
    pushq %rdi
    pushq %r8
    pushq %r9
    pushq %r10
    callq Object_init
    popq %r10
    popq %r9
    popq %r8
    popq %rdi
    popq %rsi
    popq %rcx
    popq %rdx
    movq $0, 24(%rbp)
    leaq string_const1(%rip), %rax
    movq %rax, 32(%rbp)
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
    movq %rdi, %rdi
    pushq %rdx
    pushq %rcx
    pushq %rsi
    pushq %rdi
    pushq %r8
    pushq %r9
    pushq %r10
    callq Object_init
    popq %r10
    popq %r9
    popq %r8
    popq %rdi
    popq %rsi
    popq %rcx
    popq %rdx
    movq $0, 24(%rbp)
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
    movq %rdi, %rdi
    pushq %rdx
    pushq %rcx
    pushq %rsi
    pushq %rdi
    pushq %r8
    pushq %r9
    pushq %r10
    callq Object_init
    popq %r10
    popq %r9
    popq %r8
    popq %rdi
    popq %rsi
    popq %rcx
    popq %rdx
    movq $0, 24(%rbp)
    popq %r14
    popq %r13
    popq %r12
    popq %rbx
    leave
    ret



Main_whileloop:
    pushq %rbp
    movq %rsp, %rbp
    pushq %rbx
    pushq %r12
    pushq %r13
    pushq %r14
    subq $16, %rsp
    movq %rdi, -40(%rbp)
    movq %rsi, -48(%rbp)
Main.whileloop.loop_start.2:
    movq -48(%rbp), %rax
    pushq %rax
    leaq int_const3(%rip), %rax
    addq $24, %rax
    movq (%rax), %rax
    popq %rdi
    cmpq %rax, %rdi
    setg %al
    movzbq %al, %rax

    cmpq $1, %rax
    jne Main.whileloop.loop_end.2
    movq -40(%rbp), %rax
    movq %rax, %rdi
    movq -48(%rbp), %rax
    movq %rax, %rsi
    movq 16(%rdi), %r10
    movq 24(%r10), %r10
    pushq %rdx
    pushq %rcx
    pushq %rsi
    pushq %rdi
    pushq %r8
    pushq %r9
    pushq %r10
    callq *%r10
    popq %r10
    popq %r9
    popq %r8
    popq %rdi
    popq %rsi
    popq %rcx
    popq %rdx

    movq -40(%rbp), %rax
    movq %rax, %rdi
    leaq string_const4(%rip), %rax
    addq $32, %rax
    movq %rax, %rsi
    movq 16(%rdi), %r10
    movq 16(%r10), %r10
    pushq %rdx
    pushq %rcx
    pushq %rsi
    pushq %rdi
    pushq %r8
    pushq %r9
    pushq %r10
    callq *%r10
    popq %r10
    popq %r9
    popq %r8
    popq %rdi
    popq %rsi
    popq %rcx
    popq %rdx

    movq -48(%rbp), %rax

    push %rax
    leaq int_const5(%rip), %rax
    addq $24, %rax
    movq (%rax), %rax

    popq %rdi
    subq %rax, %rdi
    movq %rdi, %rax
    movq %rax, -48(%rbp)

    jmp Main.whileloop.loop_start.2
Main.whileloop.loop_end.2:
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
    movq %rax, %rdi
    leaq int_const6(%rip), %rax
    addq $24, %rax
    movq (%rax), %rax
    movq %rax, %rsi
    movq 16(%rdi), %r10
    movq 48(%r10), %r10
    pushq %rdx
    pushq %rcx
    pushq %rsi
    pushq %rdi
    pushq %r8
    pushq %r9
    pushq %r10
    callq *%r10
    popq %r10
    popq %r9
    popq %r8
    popq %rdi
    popq %rsi
    popq %rcx
    popq %rdx
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
    movq %rdi, %rdi
    pushq %rdx
    pushq %rcx
    pushq %rsi
    pushq %rdi
    pushq %r8
    pushq %r9
    pushq %r10
    callq IO_init
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



