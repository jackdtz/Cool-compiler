(* hello-world.cl *) 
class Main inherits IO { 
  x : Int <- 3;
  y : Int <- 10;
  z : Int;
  main() : Object { 
    {
      out_string("Hello, world.\n") ;
      z <- (x + 3) * y /2;
      out_string(z);
    }
  } ; 
} ; 