class Main inherits IO {

   whileloop(x: Int) : Object{
       while x > 0 loop
       {
        out_string("haha");
        x <- x - 1;
       }
       pool
   };

   main(): Object {
     whileloop(10)
       
   };
};
