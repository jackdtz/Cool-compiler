class A inherits IO {

    init() : Object {
        out_string("init A")
    };

    toString() : Object {
        out_string("toString A called")
    };


};

class B inherits A {

    init() : Object  {
        out_string("init B")
    };

    toString() : Object {
        out_string("toString B called")
    };
    

};


class Main inherits IO {

   a : A;
   
   main(): Object {
       {
        a <- new B;
        a.toString();
       }
   };
};
