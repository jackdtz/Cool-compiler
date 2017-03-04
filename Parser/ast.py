
class Node(object):

    ops = [
        "+", "-", "*", "/", 
        "~", "=",
        "<", "<=",
        ">", ">="
    ]
    def __init__(self):
        pass

class Program(Node):
    """
    program ::= [[class; ]]+
    """
    def __init__(self, classes):
        self.classes = classes

    # def __str__(self):
    #     return (
    #         "Program\n"
    #         "\t" + [str(c) for c in self.classes]
    #     )

class Class(Node):
    """
    class ::= class TYPE [inherits TYPE] { [feature;]* }
    """
    def __init__(self, classType, features, inheritType=None):
        self.classType = classType
        self.inheritType = inheritType
        self.features = features


class Feature(Node):
    def __init__(self):
        pass

class FeatureMethod(Feature):
    """
    feature ::= ID( [ formal [, formal]* ] ) : TYPE { expr }
    """
    def __init__(self, methodName, formalParams, retType, bodyExpr):
        self.methodName = methodName
        self.formalParams = formalParams
        self.retType = retType
        self.bodyExpr = bodyExpr

class FeatureAttribute(Feature):
    """
    feature ::= ID : TYPE [ <- expr ]
    """
    def __init__(self, id, decType, init=None):
        self.id = id
        self.decType = decType
        self.init = init

class FormalParam(Node):
    """
    feature ::= ID : TYPE
    """
    def __init__(self, id, decType):
        self.id = id
        self.decType = decType

class Expr(Node):
    def __init__(self):
        pass

class AssignmentExpr(Expr):
    """
    expr ::= ID <- expr
    """
    def __init__(self, id, expr):
        self.id = id
        self.expr = expr

class Dispatch(Expr):
    """
    expr ::= expr[@TYPE].ID( [ expr [[, expr]] ] )
    """
    def __init__(self, objExpr, method, arguments, parent=None):
        self.objExpr = objExpr
        self.method = method
        self.arguments = arguments
        self.parent = parent

class MethodCall(Expr):
    """
    expr ::= ID( [ expr [, expr]* ] )
    """
    def __init__(self, id, exprs):
        self.id = id
        self.exprs = exprs

class If(Expr):
    """
    expr ::= if expr then expr else expr fi
    """
    def __init__(self, condition, thenExpr, elseExpr):
        self.condition = condition
        self.thenExpr = thenExpr
        self.elseExpr = elseExpr

class While(Expr):
    """
    expr ::= while expr loop expr pool
    """
    def __init__(self, condition, bodyExpr):
        self.condition = condition
        self.bodyExpr = bodyExpr

class Block(Expr):
    """
    expr ::= { [expr; ]+ }
    """
    def __init__(self, exprs):
        self.exprs = exprs

class LetVarDecl(Node):
    """
    expr ::= ID : TYPE <- expr
    """
    def __init__(self, id, decType, init=None):
        self.id = id
        self.decType = decType
        self.init = init

class Let(Expr):
    """
    expr ::= let ID : TYPE [ <- expr ] [, ID : TYPE [ <- expr ]]* in expr
    """
    def __init__(self, declareVars, bodyExpr):
        self.declareVars = declareVars
        self.bodyExpr = bodyExpr

class CaseAction(Node):
    """
    action ::= ID : TYPE => expr
    """
    def __init__(self, id, defType, body):
        self.id = id
        self.defType = defType
        self.body = body

class Case(Expr):
    """
    expr ::= case expr of [ID : TYPE => expr; ]+ esac
    """
    def __init__(self, cond, actions):
        self.cond = cond
        self.actions = actions

class NewConstruct(Expr):
    """
    expr ::= new Type
    """
    def __init__(self, objType):
        self.objType = objType

class IsVoid(Expr):
    """
    expr ::= isvoid expr
    """
    def __init__(self, expr):
        self.expr = expr

class BinaryOp(Expr):
    def __init__(self, e1, e2):
        self.e1 = e1
        self.e2 = e2

class Plus(BinaryOp):
    """
    expr ::= expr + expr
    """
    def __init__(self, e1, e2):
        super(Plus, self).__init__(e1, e2)

class Minus(BinaryOp):
    """
    expr ::= expr - expr
    """
    def __init__(self, e1, e2):
        super(Minus, self).__init__(e1, e2)

class Multiply(BinaryOp):
    """
    expr ::= expr * expr
    """
    def __init__(self, e1, e2):
        super(Multiply, self).__init__(e1, e2)

class Divide(BinaryOp):
    """
    expr ::= expr * expr
    """
    def __init__(self, e1, e2):
        super(Divide, self).__init__(e1, e2)

class LessThan(BinaryOp):
    """
    expr ::= expr < expr
    """
    def __init__(self, e1, e2):
        super(LessThan, self).__init__(e1, e2)

class LessEq(BinaryOp):
    """
    expr ::= expr <= expr
    """
    def __init__(self, e1, e2):
        super(LessEq, self).__init__(e1, e2)

class Eq(BinaryOp):
    """
    expr ::= expr = expr
    """
    def __init__(self, e1, e2):
        super(Eq, self).__init__(e1, e2)

class GreaterThan(BinaryOp):
    """
    expr ::= expr > expr
    """
    def __init__(self, e1, e2):
        super(GreaterThan, self).__init__(e1, e2)

class GreaterEq(BinaryOp):
    """
    expr ::= expr >= expr
    """
    def __init__(self, e1, e2):
        super(GreaterEq, self).__init__(e1, e2)

class Not(Expr):
    """
    expr ::= not expr
    """
    def __init__(self, expr):
        self.expr = expr

class Integer(Expr):
    """
    expr ::= integer
    """
    def __init__(self, ival):
        self.ival = ival

class String(Expr):
    """
    expr ::= string
    """
    def __init__(self, sval):
        self.sval = sval

class Boolean(Expr):
    """
    expr ::= boolean
    """
    def __init__(self, bval):
        self.bval = bval

class TwosComplement(Expr):
    def __init__(self, expr):
        self.expr = expr





