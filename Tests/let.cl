class Main inherits IO {
    main() : Object {
        let x : Int <- 3 in
        {
            out_int(x);
            {let x : Int <- 1 in
                out_int(x);
            };
            out_int(x);

        }
    };
};