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
    .asciz   ""

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

Main_dispatch_table:
    .quad    Object_abort
    .quad    Object_copy
    .quad    IO_out_string
    .quad    IO_out_int
    .quad    _IO_in_string
    .quad    _IO_in_int
    .quad    Main_main

Bool_dispatch_table:
    .quad    Object_abort
    .quad    Object_copy
int_const1:
    .quad    3
    .quad    4
    .quad    Int_dispatch_table
    .quad    16

int_const2:
    .quad    3
    .quad    4
    .quad    Int_dispatch_table
    .quad    17

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
    .asciz    ""
    .align    8

string_const1:
    .quad    2
    .quad    6
    .quad    String_dispatch_table
    .quad    int_const1
    .asciz    "this is true\n"
    .align    8

string_const2:
    .quad    2
    .quad    6
    .quad    String_dispatch_table
    .quad    int_const2
    .asciz    "this is false\n"
    .align    8


.text



Object_init:
    pushq %rbp
    movq %rsp, %rbp
    leave
    ret






IO_init:
    pushq %rbp
    movq %rsp, %rbp
    movq %rdi, %rdi
    callq Object_init
    leave
    ret





String_init:
    pushq %rbp
    movq %rsp, %rbp
    movq %rdi, %rdi
    callq Object_init
    leaq string_const0(%rip), %rax
    movq %rax, 32(%rbp)
    movq $0, 24(%rbp)
    leave
    ret


Int_init:
    pushq %rbp
    movq %rsp, %rbp
    movq %rdi, %rdi
    callq Object_init
    movq $0, 24(%rbp)
    leave
    ret


Bool_init:
    pushq %rbp
    movq %rsp, %rbp
    movq %rdi, %rdi
    callq Object_init
    movq $0, 24(%rbp)
    leave
    ret



Main_main:
    pushq %rbp
    movq %rsp, %rbp
    subq $16, %rsp
    movq %rdi, -8(%rbp)
    movq $1, %rax
    cmpq $1, %rax
    jne Main.main.else.0
    movq -8(%rbp), %rdi
    leaq string_const1(%rip), %rax
    addq $32, %rax
    movq %rax, %rsi
    movq 16(%rdi), %r10
    movq 16(%r10), %r10
    callq* %r10

    jmp Main.main.end.0

Main.main.else.0:
    movq -8(%rbp), %rdi
    leaq string_const2(%rip), %rax
    addq $32, %rax
    movq %rax, %rsi
    movq 16(%rdi), %r10
    movq 16(%r10), %r10
    callq* %r10

Main.main.end.0:
    addq $16, %rsp
    leave
    ret

Main_init:
    pushq %rbp
    movq %rsp, %rbp
    movq %rdi, %rdi
    callq IO_init
    leave
    ret



