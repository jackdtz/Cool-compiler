import cool_ast as AST
from lexer import *
import ply3.ply.yacc as yacc


class Parser(object):


    precedence = (
        ('right', 'ASSIGN'),
        ('left', 'NOT'),
        ('nonassoc', 'LESSTHAN', 'LESSEQ', 'EQUAL', 'GREATERTHAN', 'GREATEREQ'),
        ('left', 'PLUS', 'MINUS'),
        ('left', 'MULTIPLY', 'DIVIDE'),
        ('right', 'ISVOID'),
        ('right', 'UNARY_COMP'),
        ('left', 'ALT'),
        ('left', 'DOT'),
    )

    def __init__(self):
        self.tokens = None
        self.parser = None
        self.src = None
        self.lexer = make_lexer()
        self.error_list = []
        self.start = 'program'
        self.tracking = False

    @staticmethod
    def findpos(input, token):
        last_cr = input.rfind('\n', 0, token.lexpos)

        if last_cr < 0:
            last_cr = 0

        return token.lexpos - last_cr + 1

    def build(self):
        self.tokens = self.lexer.tokens
        self.parser = yacc.yacc(module=self)

    def parse(self, src):
        self.src = src
        return self.parser.parse(src)


    def p_error(self, parse):

        if parse is None:
            print("Error! Unexpected end of input!")
        else:
            msg = "Syntax error near \"{}\" at line: {}, position: {}".format(parse.value, parse.lineno, self.findpos(self.src, parse))
            self.error_list.append(msg)
            # self.parser.errok()
            # print(self.error_list)
            print(msg)

    def p_program(self, p):
        """
        program : classes
        """
        p[0] = AST.Program(p[1])

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
            p[0] = AST.Class(p[2], p[4])
        else:
            p[0] = AST.Class(p[2], p[6], inheritType=p[4])

    def p_features(self, p):
        """
        features : features feature
                 | feature
                 | empty
        """ 
        if len(p) == 3:
            p[1].append(p[2])
            p[0] = p[1]
        elif len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = []
    
    def p_feature(self, p):
        """
        feature : feature_method 
                | feature_attribute
        """
        p[0] = p[1]

    def p_feature_method(self, p):
        """
        feature_method : ID LPAREN formals RPAREN COLON TYPE_ID LBRACE expression RBRACE SEMICOLON
        """
        p[0] = AST.FeatureMethodDecl(p[1], p[3], p[6], p[8])

    def p_feature_attribute(self, p):
        """
        feature_attribute : ID COLON TYPE_ID SEMICOLON
                          | ID COLON TYPE_ID ASSIGN expression SEMICOLON
        """
        if len(p) == 5:
            p[0] = AST.FeatureAttribute(p[1], p[3])
        else:
            p[0] = AST.FeatureAttribute(p[1], p[3], init=p[5])


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
        p[0] = AST.FormalParam(p[1], p[3])


    def p_expression_assignment(self, p):
        """
        expression : ID ASSIGN expression
        """
        p[0] = AST.AssignmentExpr(p[1], p[3])
    
    def p_expression_dispatch(self, p):
        """
        expression : expression DOT ID LPAREN arguments RPAREN
                   | expression ALT TYPE_ID DOT ID LPAREN arguments RPAREN
        """
        if len(p) == 7:
            p[0] = AST.Dispatch(p[1], p[3], p[5])
        else:
            p[0] = AST.Dispatch(p[1], p[5], p[7], parent=p[3])
    
    def p_expression_method_call(self, p):
        """
        expression : ID LPAREN arguments RPAREN
        """
        p[0] = AST.MethodCall(p[1], p[3])

    def p_arguments(self, p):
        """
        arguments : arguments COMMA argument
                  | argument
                  | empty
        """
        if len(p) == 4:
            p[1].append(p[3])
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
        p[0] = AST.If(p[2], p[4], p[6])        

    def p_expression_while(self, p):
        """
        expression : WHILE expression LOOP expression POOL
        """
        p[0] = AST.While(p[2], p[4])

    def p_expression_block(self, p):
        """
        expression : LBRACE expressions RBRACE
        """
        p[0] = AST.Block(p[2])
    
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
        p[0] = AST.Let(p[2], p[4])

    def p_let_var_decls(self, p):
        """
        let_var_decls : let_var_decls COMMA let_var_decl 
                      | let_var_decl
        """
        if len(p) == 4:
            p[1].append(p[3])
            p[0] = p[1]
        elif len(p) == 2:
            p[0] = [p[1]]

    def p_let_var_decl(self, p):
        """
        let_var_decl : ID COLON TYPE_ID ASSIGN expression
                     | ID COLON TYPE_ID 
        """
        if len(p) == 6:
            p[0] = AST.LetVarDecl(p[1], p[3], init=p[5])
        elif len(p) == 4:
            p[0] = AST.LetVarDecl(p[1], p[3])
        
    def p_expression_case(self, p):
        """
        expression : CASE expression OF case_actions ESAC
        """
        p[0] = AST.Case(p[2], p[4])
    
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
        p[0] = AST.CaseAction(p[1], p[3], p[5])
    
    def p_expression_new(self, p):
        """
        expression : NEW TYPE_ID
        """
        p[0] = AST.NewConstruct(p[2])

    def p_expression_isvoid(self, p):
        """
        expression : ISVOID expression
        """
        p[0] = AST.IsVoid(p[2])

    def p_expression_math_op(self, p):
        """
        expression : expression PLUS expression
                   | expression MINUS expression
                   | expression MULTIPLY expression
                   | expression DIVIDE expression
                   | UNARY_COMP expression
        """
        if p[2] == "+":
            p[0] = AST.Plus(p[1], p[3])
        elif p[2] == '-':
            p[0] = AST.Minus(p[1], p[3])
        elif p[2] == '*':
            p[0] = AST.Multiply(p[1], p[3])
        elif p[2] == '/':
            p[0] = AST.Divide(p[1], p[3])
        elif p[1] == "~":
            p[0] = AST.TwosComplement(p[2])

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
            p[0] = AST.GreaterThan(p[1], p[3])
        elif p[2] == '<=':
            p[0] = AST.GreaterEq(p[1], p[3])
        elif p[2] == '=':
            p[0] = AST.Eq(p[1], p[3])
        elif p[2] == '>':
            p[0] = AST.GreaterThan(p[1], p[3])
        elif p[1] == ">=":
            p[0] = AST.GreaterEq(p[1], p[3])
        else:
            p[0] = AST.Not(p[2])

    def p_expression_paren(self, p):
        """
        expression : LPAREN expression RPAREN
        """
        p[0] = AST.ParenExpr(p[2])

    def p_expression_integer(self, p):
        """
        expression : INTEGER
        """
        p[0] = AST.Integer(p[1])
    
    def p_expression_string(self, p):
        """
        expression : STRING
        """
        p[0] = AST.String(p[1])

    def p_expression_boolean(self, p):
        """
        expression : BOOLEAN
        """
        p[0] = AST.Boolean(p[1])

    def p_expression_self(self, p):
        """
        expression : SELF
        """
        p[0] = AST.Self()

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
    import sys, os, glob

    root_path = '/Users/Jack/Documents/programming/python/coolCompiler'
    test_folder = root_path + '/Tests'       

    parser = make_parser() 

    for filename in os.listdir(test_folder):
        if filename.endswith('.cl'):
            file_path = test_folder + "/" + filename
            print("-------------------Testing parser with file {}-------------------".format(filename))
            with open(file_path, encoding='utf-8') as file:
                cool_program_code = file.read()
                parse_result = parser.parse(cool_program_code)
                # print(parse_result)
                
    
        


    # with open("Tests/helloworld.cl") as file:
    #         cool_program_code = file.read()

    # parse_result = parser.parse(cool_program_code)
    # print(parse_result)


