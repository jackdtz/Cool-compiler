class Main inherits IO{
	x : Int;
	main () : Object {
		{
			x <- 9;
			while x<10 loop 
			{
				out_int(x) ;
				x <- x + 1;
			}
			pool;
		}
	};
};
