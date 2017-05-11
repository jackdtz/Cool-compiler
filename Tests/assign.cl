class Main inherits IO{
	x : Int;
	main () : Object {
		{
			out_int(x);
			x <- x + 1;
			out_int(x);
		}
	};
};
