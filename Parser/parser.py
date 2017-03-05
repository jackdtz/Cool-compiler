from ast import *
from lexer import *
import ply3.ply.yacc as yacc


class Parser(object):


    precedence = (
        ('right', 'ASSIGN'),
        ('right', 'NOT'),
        ('nonassoc', 'LESSTHAN', 'LESSEQ', 'EQUAL', 'GREATERTHAN', 'GREATEREQ'),
        ('left', 'PLUS', 'MINUS'),
        ('left', 'MULTIPLY', 'DIVIDE'),
        ('right', 'ISVOID'),
        ('right', 'UNARY_COMP'),
        ('left', 'ALT'),
        ('left', 'DOT')
    )

    def __init__(self):
        self.tokens = None
        self.parser = None
        self.lexer = make_lexer()
        self.error_list = []

    def build(self):
        self.tokens = self.lexer.tokens
        self.parser = yacc.yacc(module=self)

    def parse(self, src):
        return self.parser.parse(src)


    def p_error(self, parse):

        if parse is None:
            print("Error! Unexpected end of input!")
            [print(e) for e in self.error_list]
        else:
            error = "Syntax error! Line: {}, position: {}, character: {}, type: {}".format(
                parse.lineno, parse.lexpos, parse.value, parse.type)
            self.error_list.append(error)
            self.parser.errok()

    def p_program(self, p):
        """
        program : classes
        """
        p[0] = Program(p[1])

    def p_classes(self, p):
        """
        classes : classes class
                | class
        """
        if len(p) == 3:
            p[1].append(p[2])
            p[0] = p[1]
        else:
            p[0] = [p[1]]

    def p_class(self, p):
        """
        class : CLASS TYPE_ID LBRACE features RBRACE SEMICOLON
              | CLASS TYPE_ID INHERITS TYPE_ID LBRACE features RBRACE SEMICOLON 
        """
        if len(p) == 7:
            p[0] = Class(p[2], p[4])
        else:
            p[0] = Class(p[2], p[6], inheritType=p[4])

    def p_features(self, p):
        """
        features : features feature SEMICOLON 
                 | feature SEMICOLON
                 | empty
        """ 

        if len(p) == 4:
            p[1].append(p[2])
            p[0] = p[1]
        elif len(p) == 3:
            p[0] = [p[1]]
        else:
            p[0] = []
    
    def p_feature(self, p):
        """
        feature : ID LPAREN formals RPAREN COLON TYPE_ID LBRACE expression RBRACE
                | ID COLON TYPE_ID 
                | ID COLON TYPE_ID ASSIGN expression
        """
        if len(p) == 10:
            p[0] = FeatureMethodDecl(p[1], p[3], p[6], p[8])
        elif len(p) == 4:
            p[0] = FeatureAttribute(p[1], p[3])
        else:
            p[0] = FeatureAttribute(p[1], p[3], init=p[5])

    def p_formals(self, p):
        """
        formals : formals COMMA formal
                | formal
                | empty
        """
        if len(p) == 4:
            p[1].append(p[3])
            p[0] = p[1]
        elif len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = []
    
    def p_formal(self, p):
        """
        formal : ID COLON TYPE_ID
        """
        p[0] = FormalParam(p[1], p[3])

    def p_expression_assignment(self, p):
        """
        expression : ID ASSIGN expression
        """
        p[0] = AssignmentExpr(p[1], p[3])
    
    def p_expression_dispatch(self, p):
        """
        expression : expression DOT ID LPAREN arguments RPAREN
                   | expression ALT TYPE_ID DOT ID LPAREN arguments RPAREN
        """
        if len(p) == 7:
            p[0] = Dispatch(p[1], p[3], p[5])
        else:
            p[0] = Dispatch(p[1], p[5], p[7], parent=p[3])
    
    def p_expression_method_call(self, p):
        """
        expression : ID LPAREN arguments RPAREN
        """
        p[0] = MethodCall(p[1], p[3])

    def p_arguments(self, p):
        """
        arguments : arguments COMMA argument
                  | argument
                  | empty
        """
        if len(p) == 4:
            p[3].append(p[1])
            p[0] = p[1]
        elif len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = []
        
    def p_argument(self, p):
        """
        argument : expression
        """
        p[0] = p[1]

    def p_expression_if(self, p):
        """
        expression : IF expression THEN expression ELSE expression FI
        """
        p[0] = If(p[2], p[4], p[6])        

    def p_expression_while(self, p):
        """
        expression : WHILE expression LOOP expression POOL
        """
        p[0] = While(p[2], p[4])

    def p_expression_block(self, p):
        """
        expression : LBRACE expressions RBRACE
        """
        p[0] = Block(p[2])
    
    def p_expressions(self, p):
        """
        expressions : expressions expression SEMICOLON
                    | expression SEMICOLON
        """
        if len(p) == 4:
            p[1].append(p[2])
            p[0] = p[1]
        elif len(p) == 3:
            p[0] = [p[1]]
        else:
            p[0] = []
    
    def p_expression_let(self, p):
        """
        expression : LET let_var_decls IN expression        
        """
        p[0] = Let([p[2]] + p[3], p[5])

    def p_let_var_decls(self, p):
        """
        let_var_decls : let_var_decls COMMA let_var_decl 
                      | let_var_decl
        """
        if len(p) == 4:
            p[3].append(p[2])
            p[0] = p[3]
        elif len(p) == 3:
            p[0] = [p[2]]
        else:
            p[0] = []

    def p_let_var_decl(self, p):
        """
        let_var_decl : ID COLON TYPE_ID ASSIGN expression
                     | ID COLON TYPE_ID 
        """
        if len(p) == 6:
            p[0] = LetVarDecl(p[1], p[3], init=p[5])
        elif len(p) == 4:
            p[0] = LetVarDecl(p[1], p[3])
        
    def p_expression_case(self, p):
        """
        expression : CASE expression OF case_actions ESAC
        """
        p[0] = Case(p[2], p[4])
    
    def p_case_actions(self, p):
        """
        case_actions : case_action case_actions
                     | case_action
        """
        if len(p) == 3:
            p[2].append(p[1])
            p[0] = p[2]
        else:
            p[0] = [p[1]]

    def p_case_action(self, p):
        """
        case_action : ID COLON TYPE_ID ARROW expression SEMICOLON
        """
        p[0] = CaseAction(p[1], p[3], p[5])
    
    def p_expression_new(self, p):
        """
        expression : NEW TYPE_ID
        """
        p[0] = NewConstruct(p[2])

    def p_expression_isvoid(self, p):
        """
        expression : ISVOID expression
        """
        p[0] = IsVoid(p[2])

    def p_expression_math_op(self, p):
        """
        expression : expression PLUS expression
                   | expression MINUS expression
                   | expression MULTIPLY expression
                   | expression DIVIDE expression
                   | UNARY_COMP expression
        """
        if p[2] == "+":
            p[0] = Plus(p[1], p[3])
        elif p[2] == '-':
            p[0] = Minus(p[1], p[3])
        elif p[2] == '*':
            p[0] = Multiply(p[1], p[3])
        elif p[2] == '/':
            p[0] = Divide(p[1], p[3])
        elif p[1] == "~":
            p[0] = TwosComplement(p[2])

    def p_expression_comparison(self, p):
        """
        expression : expression LESSTHAN expression
                   | expression LESSEQ expression
                   | expression EQUAL expression
                   | expression GREATERTHAN expression
                   | expression GREATEREQ expression
                   | NOT expression
        """
        if p[2] == "<":
            p[0] = GreaterThan(p[1], p[3])
        elif p[2] == '<=':
            p[0] = GreaterEq(p[1], p[3])
        elif p[2] == '=':
            p[0] = Eq(p[1], p[3])
        elif p[2] == '>':
            p[0] = GreaterThan(p[1], p[3])
        elif p[1] == ">=":
            p[0] = GreaterEq(p[1], p[3])
        else:
            p[0] = Not(p[2])

    def p_expression_paren(self, p):
        """
        expression : LPAREN expression RPAREN
        """
        p[0] = p[2]

    def p_expression_integer(self, p):
        """
        expression : INTEGER
        """
        p[0] = Integer(p[1])
    
    def p_expression_string(self, p):
        """
        expression : STRING
        """
        p[0] = String(p[1])

    def p_expression_boolean(self, p):
        """
        expression : BOOLEAN
        """
        p[0] = Boolean(p[1])

    def p_expression_self(self, p):
        """
        expression : SELF
        """
        p[0] = Self()

    def p_expression_id(self, p):
        """
        expression : ID
        """
        p[0] = p[1]

    def p_empty(self, p):
        """
        empty :
        """
        p[0] = None

    

def make_parser():
    parser = Parser()
    parser.build()
    return parser


if __name__ == "__main__":
    import sys

    parser = make_parser()        

    with open("Tests/helloworld.cl") as file:
            cool_program_code = file.read()

    parse_result = parser.parse(cool_program_code)
    print(parse_result)
    
        





