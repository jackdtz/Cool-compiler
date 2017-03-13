
from ply3.ply import lex as lex

from ply3.ply.lex import TOKEN

class Scanner(object):
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_LBRACE = r'\{'
    t_RBRACE = r'\}'
    t_DOT = r'\.'
    t_COLON = r'\:'
    t_SEMICOLON = r';'
    t_COMMA = r'\,'
    t_PLUS = r'\+'
    t_MINUS = r'\-'
    t_MULTIPLY = r'\*'
    t_DIVIDE = r'\/'
    t_LESSTHAN = r'\<'
    t_LESSEQ = r'\<\='
    t_EQUAL = r'\='
    t_ASSIGN = r'\<\-'
    t_GREATERTHAN = r'\>'
    t_GREATEREQ = r'\>\='
    t_STRING = r'\"([^\"\\]|\\.)*\"'
    t_ARROW = r'\=\>'
    t_UNARY_COMP = r'\~'
    t_ALT = r'\@'

    def __init__(self):
        self.tokens = ()
        self.lexer = None

    def build(self):
        self.tokens = self.token_types + tuple(self.reserved_keywords.values())

        lexer = lex.lex(object=self)
        return lexer

    @property
    def reserved_keywords(self):
        return {
            "case": "CASE",
            "class": "CLASS",
            "else": "ELSE",
            "esac": "ESAC",
            "fi": "FI",
            "if": "IF",
            "in": "IN",
            "inherits": "INHERITS",
            "isvoid": "ISVOID",
            "let": "LET",
            "loop": "LOOP",
            "new": "NEW",
            "of": "OF",
            "pool": "POOL",
            "self": "SELF",
            "then": "THEN",
            "while": "WHILE",
            "not" : "NOT"
        }

    @property
    def token_types(self):
        return (
           # identifier
           "ID", "TYPE_ID",

           # primitive type
           "INTEGER", "STRING", "BOOLEAN",

           # literals
           "LPAREN", "RPAREN", "LBRACE", "RBRACE", "COLON", "SEMICOLON", "COMMA", "ALT", "DOT",

           # operator
           "LESSTHAN", "LESSEQ", "EQUAL", "GREATERTHAN", "GREATEREQ", "PLUS", "MINUS", "MULTIPLY", "DIVIDE", "ASSIGN",

           "ARROW", "UNARY_COMP"
        )


    t_ignore = ' \t\r\f\v'
    t_ignore_COMMENT_DASH = r'\-\-.*'
    # t_ignore_COMMENT = r'\(\*(.|\n)*\*\)'


    @TOKEN(r'\(\*(.|\n)*?\*\)')
    def t_COMMENT(self, token):
        token.lexer.lineno += token.value.count('\n') 
    

    @TOKEN(r'true|false')
    def t_BOOLEAN(self, token):
        token.value = True if token.value == 'true' else False
        return token

    @TOKEN(r'\d+')
    def t_INTEGER(self, token):
        token.value = int(token.value)
        return token

    @TOKEN(r'[A-Z][A-Za-z0-9_]*')
    def t_TYPE_ID(self, token):
        token.type = self.reserved_keywords.get(token.value, 'TYPE_ID')
        return token

    @TOKEN(r'[a-z][a-zA-Z0-9_]*')
    def t_OBJECT_ID(self, token):
        token.type = self.reserved_keywords.get(token.value, 'ID')
        return token
    
    @TOKEN(r'\n')
    def t_newline(self,token):
        token.lexer.lineno += 1

    @TOKEN(r'\n+')
    def t_newlines(self,token):
        token.lexer.lineno += len(token.value)

    def t_error(self, token):
        print("Illegal character '{}' at line {}".format(token.value[0], token.lineno))
        token.lexer.skip(1)

    def t_eof(self, token):
        token.lexer.lineno = 1
        token.lexpos = 0

def make_lexer():
    lexer = Scanner()
    lexer.build()
    return lexer

if __name__ == "__main__":
    import sys
    with open("Tests/test1.cl", encoding="utf-8") as file:
        cool_program_code = file.read()
        # print(cool_program_code)

    lexer = Scanner().build()
    lexer.input(cool_program_code)
    for token in lexer:
        print(token)


