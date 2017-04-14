class Main inherits IO{
	x : Int <- 2 + 3;
	main () : Object {
		{
			while x<9000 loop 
			{
				out_int(x) ;
				x <- x + 1;
			}
			pool;
		}
	};
};
