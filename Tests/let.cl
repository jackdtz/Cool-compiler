class Let {
    main() : Int {
        let x : Int in
        {
            x;
            {let x : Int <- 1 in
                x;
            };
            x;
        }
    };
};