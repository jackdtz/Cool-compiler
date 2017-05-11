class Main inherits IO {

    fib(x : Int) : Int {
        if x < 2
        then x
        else fib(x - 1) + fib(x - 2)
        fi
    };

    main() : Object {
        out_int(fib(10))
    };
};