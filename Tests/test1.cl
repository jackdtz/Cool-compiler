-- example of static and dynamic type differing for a dispatch

class Book inherits IO {
    title : String;
    author : String;

    initBook(title_p : String, author_p : String) : Book {
        {
            title <- title_p;
            author <- author_p;
            self;
        }
    };

    print() : Book {
        {
            out_string("title:      ").out_string(title).out_string("\n");
            out_string("author:     ").out_string(author).out_string("\n");
            self;
        }
    };
};