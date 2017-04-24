
obj_tag = 0
obj_size = 8
obj_disp = 16
obj_attr = 24
string_str_offset = 32

.data
    .globl _main
    .globl Object_abort
    .globl Object_copy
    .globl IO_out_string
    .globl IO_out_int
    .globl IO_in_string
    .globl IO_in_int
    .globl String_length
    .globl String_concat
    .globl String_substr



    _term_msg:	.asciz "COOL program successfully executed"
    _object_abort_msg:  .asciz "Program aborted with exit code 1\n"


.text
    
    Object_abort: 
        pushq %rbp
        movq %rsp, %rbp

        subq $8, %rsp
        movq %rdi, 8(%rsp)      # save self object
        leaq _object_abort_msg(%rip), %rdi 
        callq _print_string
        movq $60, %rdi
        syscall

    # Object_type_name:
    #     pushq %rbp
    #     movq %rbp, %rsp

    #     subq 8, %rsp
    #     movq %rdi, 8(%rsp)      # save self object

    Object_copy:
        pushq %rbp
        movq %rsp, %rbp

        # subq $16, %rsp              # os x is 16 byte aligned
        # movq %rdi, 16(%rsp)          # save self address

        movq %rdi, %rbx             # save the object address into rbx

        movq obj_size(%rdi), %rax   # get object size
        imul $8, %rax          
        movq %rax, %rdi 
        call _malloc               # allocate memory, and address in stored in rax

        # rbx old object address
        # rax new object address
        # rdi object size, mutiply of 8
        # rcx temp reg

        # set rdx to counter, starting from 0, increment by 8
        movq $0, %rdx

        # move object size into rdi, then multiply 8 to get the actual bytes
        movq obj_size(%rbx), %rdi
        imul $8, %rdi

        jmp start_loop



    start_loop:
        cmpq %rdx, %rdi
        jle end_loop

        movq (%rdx, %rbx, 1), %rcx
        movq %rcx, (%rdx, %rax, 1)

        addq $8, %rdx
        jmp start_loop

    end_loop:
        leave 
        ret

    IO_out_string:
        pushq %rbp
        movq %rsp, %rbp

        subq $16, %rsp
        movq %rdi, 0(%rsp)

        movq %rsi, %rdi
        callq _print_string

        movq 0(%rsp), %rax
        addq $16, %rsp

        leave
        ret

    IO_out_int:
        pushq %rbp
        movq %rsp, %rbp

        movq %rsi, %rdi
        callq _print_int

        leave
        ret

    String_length:
        pushq %rbp
        movq %rsp, %rbp

        addq $string_str_offset, %rdi

        callq _string_length

        leave
        ret   

    String_concat:

        pushq %rbp
        movq %rsp, %rbp

        subq $8, %rsp
        movq %rdi, 8(%rsp)

        movq %rsi, %rdi
        movq %rdx, %rsi
        callq _string_concat

        addq $8, %rsp
        leave
        ret

    String_substr:

        pushq %rbp
        movq %rsp, %rbp

        subq $8, %rsp
        movq %rdi, 8(%rsp)

        movq %rsi, %rdi
        movq %rdx, %rsi
        movq %rcx, %rdx
        callq _string_concat

        addq $8, %rsp
        leave
        ret

_main:
    pushq %rbp
    movq %rsp, %rbp

    leaq Main_protoObj(%rip), %rdi
    callq Object_copy                # copy main proto object
    subq $16, %rsp                    # save the main object on the stack
    movq %rax, 16(%rsp)
    movq %rax, %rdi                 # set rdi point to SELF
    callq Main_init

    movq 16(%rsp), %rdi
    callq Main_main

    leaq _term_msg(%rip), %rdi
    callq _print_string

    addq $16, %rsp                    # restore stack

    leave
    ret






