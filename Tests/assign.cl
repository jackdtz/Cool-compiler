class Main inherits IO{
	x : Int;
	main () : Object {
		{
			while x<10 loop 
			{
				out_int(x) ;
				x <- x + 1;
			}
			pool;
		}
	};
};
