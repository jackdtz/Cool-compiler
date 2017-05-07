class Main inherits IO {

   i : String;
   
   main(): Object {
       {
           out_string("enter a string\n");
           i <- in_string();
           out_string(i.substr(0, 5));
       }
    
   };
};
