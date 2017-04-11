
obj_tag = 0
obj_size = 8
obj_disp = 16
obj_attr = 24

.data



    _term_msg:	.asciz "COOL program successfully executed\n"
    _object_abort_msg:  .asciz "Program aborted with exit code 1\n"


.text
    .globl _main
    .globl Object_abort
    .globl Object_type_name
    .globl Object_copy
    
    Object_abort: 
        pushq %rbp
        movq %rbp, %rsp

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
        movq %rbp, %rsp

        subq $8, %rsp
        movq %rdi, 8(%rsp)          # save self address
        movq obj_size(%rdi), %rax   # get object size
        imul $8, %rax          
        movq %rax, %rdi 
        callq _malloc               # allocate memory, and address in stored in rax

        
        
        # rsi old object address
        # rax new object address
        # rdi object size, mutiply of 8

        # rcx temp reg

        # copy object tag
        movq 0(%rsi), %rcx
        movq %rcx, 0(%rax)

        # set rdx to counter, starting from 8
        movq $8, %rdx

        # add 8 to object size, since we are starting from 8
        addq $8, %rdi

        start_loop:
            cmpq %rdx, %rdi
            jle end_loop

            movq (%rdx, %rsi, 1), %rcx
            movq %rcx, (%rdx, %rax, 1)

            addq $8, %rdx
            jmp start_loop

        end_loop:
            leave 
            ret



    IO_out_string:
        pushq %rbp
        movq %rbp, %rsp

        subq 8, %rsp
        movq %rdi, 8(%rsp)

        movq %rsi, %rdi
        callq _print_string

        movq 8(%rsp), %rax
        addq 8, %rsp

        leave
        ret

    IO_out_int:
        pushq %rbp
        movq %rbp, %rsp

        subq 8, %rsp
        movq %rdi, 8(%rsp)

        movq %rsi, %rdi
        callq _print_int

        movq 8(%rsp), %rax

        addq 8, %rsp

        leave
        ret

    String_length:
        pushq %rbp
        movq %rbp, %rsp

        subq 8, %rsp
        movq %rdi, 8(%rsp)

        movq %rsi, %rdi
        callq _string_length

        addq 8, %rsp
        leave
        ret   

    String_concat:

        pushq %rbp
        movq %rbp, %rsp

        subq 8, %rsp
        movq %rdi, 8(%rsp)

        movq %rsi, %rdi
        movq %rdx, %rsi
        callq _string_concat

        addq 8, %rsp
        leave
        ret

    String_substr:

        pushq %rbp
        movq %rbp, %rsp

        subq 8, %rsp
        movq %rdi, 8(%rsp)

        movq %rsi, %rdi
        movq %rdx, %rsi
        movq %rcx, %rdx
        callq _string_concat

        addq 8, %rsp
        leave
        ret

        





    


    


_main:
    leaq Main_protoObj(%rip), %rdi
    callq Object_copy                # copy main proto object
    subq 8, %rsp                    # save the main object on the stack
    movq %rax, 8(%rsp)
    movq %rax, %rdi                 # set rdi point to SELF
    callq Main_init
    callq Main_main

    addq 8, %rsp                    # restore stack
    
    leaq _term_msg(%rip), %rax
    callq _print_string



