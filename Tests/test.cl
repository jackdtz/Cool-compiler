class Main {
    a : A <- new B;
	main (): Object {
		a.toString()
	};
};

class A inherits IO {
	toString() : Object { out_string("class A") };
};

class B inherits A {
	toString() : Object { out_string("class B") };
};
