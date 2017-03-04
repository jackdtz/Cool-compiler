
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

    def __str__(self):
        return "\n".join([str(c) for c in self.classes])
     

class Class(Node):
    """
    class ::= class TYPE [inherits TYPE] { [feature;]* }
    """
    def __init__(self, classType, features, inheritType=None):
        self.classType = classType
        self.inheritType = inheritType
        self.features = features

    def __str__(self):
        
        if self.features != None:
            features = ", ".join([str(f) for f in self.features])
        else:
            features = ""  

        if self.inheritType:
            return "class {} inherits {} ( {} );".format(str(self.classType), str(self.inheritType), features)
        else:
            return "class {} (\n {} \n);".format(str(self.classType), features)




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

    def __str__(self):
        if len(self.formalParams) == 1 and self.formalParams[0] == None:
            params = ""     
        else:
            params = ", ".join([str(f) for f in self.formalParams])

        
        return "{}({}) : {} ( {} );".format(str(self.methodName), params , str(self.retType), str(self.bodyExpr))

class FeatureAttribute(Feature):
    """
    feature ::= ID : TYPE [ <- expr ]
    """
    def __init__(self, id, decType, init=None):
        self.id = id
        self.decType = decType
        self.init = init

    def __str__(self):
        if self.init:
            return "{} : {} <- {}".format(str(self.id), str(self.decType), str(self.init))
        else:
            return "{} : {}".format(str(self.id), str(self.decType))


class FormalParam(Node):
    """
    feature ::= ID : TYPE
    """
    def __init__(self, id, decType):
        self.id = id
        self.decType = decType

    def __str__(self):
        return "{} : {}".format(str(self.id), str(self.decType))

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

    def __str__(self):
        return "{} <- {}".format(str(self.id), str(self.expr))

class Dispatch(Expr):
    """
    expr ::= expr[@TYPE].ID( [ expr [[, expr]] ] )
    """
    def __init__(self, objExpr, method, arguments, parent=None):
        self.objExpr = objExpr
        self.method = method
        self.arguments = arguments
        self.parent = parent

    def __str__(self):


        if len(self.arguments) == 1 and self.arguments[0] == None:
            arguments = ""
        else:
            arguments = ", ".join([str(arg) for arg in self.arguments]) 

        if self.parent:
            return "{}@{}.{}({})".format(str(self.objExpr), str(self.parent), str(self.method), arguments)
        else:
            return "{}.{}({})".format(str(self.objExpr), str(self.method), arguments)

class MethodCall(Expr):
    """
    expr ::= ID( [ expr [, expr]* ] )
    """
    def __init__(self, id, exprs):
        self.id = id
        self.exprs = exprs

    def __str__(self):
        # print(self.exprs)
        return "{}({})".format(str(self.id), ", ".join([str(e) for e in self.exprs]))

class If(Expr):
    """
    expr ::= if expr then expr else expr fi
    """
    def __init__(self, cnd, thn, els):
        self.cnd = cnd
        self.thn = thn
        self.els = els

    def __str__(self):
        return "if {} then {} else {} fi".format(str(self.cnd), str(self.thn), str(self.els))

class While(Expr):
    """
    expr ::= while expr loop expr pool
    """
    def __init__(self, condition, bodyExpr):
        self.condition = condition
        self.bodyExpr = bodyExpr

    def __str__(self):
        return "while {} loop {} pool".format(str(self.condition), str(self.bodyExpr))

class Block(Expr):
    """
    expr ::= { [expr; ]+ }
    """
    def __init__(self, exprs):
        self.exprs = exprs

    def __str__(self):
        return "( {} )".format("\n".join([str(e) + ";" for e in self.exprs]))

class LetVarDecl(Node):
    """
    expr ::= ID : TYPE <- expr
    """
    def __init__(self, id, decType, init=None):
        self.id = id
        self.decType = decType
        self.init = init

    def __str__(self):
        return "{} : {} <- {}".format(str(self.id), str(self.decType), str(self.init))

class Let(Expr):
    """
    expr ::= let ID : TYPE [ <- expr ] [, ID : TYPE [ <- expr ]]* in expr
    """
    def __init__(self, declareVars, bodyExpr):
        self.declareVars = declareVars
        self.bodyExpr = bodyExpr

    def __str__(self):
        return "let {} \tin \t{}\n".format("\n".join(["\t" + str(decl) + "\n" for decl in self.declareVars]), str(self.bodyExpr))
        

class CaseAction(Node):
    """
    action ::= ID : TYPE => expr
    """
    def __init__(self, id, defType, body):
        self.id = id
        self.defType = defType
        self.body = body

    def __str__(self):
        return "{} : {} => {}".format(str(self.id), str(self.defType), str(self.body))

class Case(Expr):
    """
    expr ::= case expr of [ID : TYPE => expr; ]+ esac
    """
    def __init__(self, cond, actions):
        self.cond = cond
        self.actions = actions

    def __str__(self):
        return (
            "case {} of\n"
            "{}"
            "esac"
        ).format(str(self.cond), ["\t" + str(action) + "\n" for action in self.actions])

class NewConstruct(Expr):
    """
    expr ::= new Type
    """
    def __init__(self, objType):
        self.objType = objType

    def __str__(self):
        return "new " + str(self.objType)

class IsVoid(Expr):
    """
    expr ::= isvoid expr
    """
    def __init__(self, expr):
        self.expr = expr

    def __str__(self):
        return "isvoid " + str(self.expr)

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

    def __str__(self):
        return str(self.e1) + " + " + str(self.e2)

class Minus(BinaryOp):
    """
    expr ::= expr - expr
    """
    def __init__(self, e1, e2):
        super(Minus, self).__init__(e1, e2)

    def __str__(self):
        return str(self.e1) + " - " + str(self.e2)

class Multiply(BinaryOp):
    """
    expr ::= expr * expr
    """
    def __init__(self, e1, e2):
        super(Multiply, self).__init__(e1, e2)

    def __str__(self):
        return str(self.e1) + " * " + str(self.e2)

class Divide(BinaryOp):
    """
    expr ::= expr / expr
    """
    def __init__(self, e1, e2):
        super(Divide, self).__init__(e1, e2)

    def __str__(self):
        return str(self.e1) + " / " + str(self.e2)

class LessThan(BinaryOp):
    """
    expr ::= expr < expr
    """
    def __init__(self, e1, e2):
        super(LessThan, self).__init__(e1, e2)

    def __str__(self):
        return str(self.e1) + " < " + str(self.e2)

class LessEq(BinaryOp):
    """
    expr ::= expr <= expr
    """
    def __init__(self, e1, e2):
        super(LessEq, self).__init__(e1, e2)

    def __str__(self):
        return str(self.e1) + " <= " + str(self.e2)

class Eq(BinaryOp):
    """
    expr ::= expr = expr
    """
    def __init__(self, e1, e2):
        super(Eq, self).__init__(e1, e2)

    def __str__(self):
        return str(self.e1) + " = " + str(self.e2)

class GreaterThan(BinaryOp):
    """
    expr ::= expr > expr
    """
    def __init__(self, e1, e2):
        super(GreaterThan, self).__init__(e1, e2)
    
    def __str__(self):
        return str(self.e1) + " > " + str(self.e2)

class GreaterEq(BinaryOp):
    """
    expr ::= expr >= expr
    """
    def __init__(self, e1, e2):
        super(GreaterEq, self).__init__(e1, e2)

    def __str__(self):
        return str(self.e1) + " >= " + str(self.e2)

class Not(Expr):
    """
    expr ::= not expr
    """
    def __init__(self, expr):
        self.expr = expr

    def __str__(self):
        return "not" + str(self.expr)

class Integer(Expr):
    """
    expr ::= integer
    """
    def __init__(self, ival):
        self.ival = ival

    def __str__(self):
        return str(self.ival)
    

class String(Expr):
    """
    expr ::= string
    """
    def __init__(self, sval):
        self.sval = sval
    
    def __str__(self):
        return str(self.sval)

class Boolean(Expr):
    """
    expr ::= boolean
    """
    def __init__(self, bval):
        self.bval = bval

    def __str__(self):
        return str(self.bval)

class Self(Expr):
    """
    expr ::= self
    """
    def __init__(self):
        pass

    def __str__(self):
        return "self"

class Id(Expr):
    """
    expr ::= ID
    """
    def __init__(self, id):
        self.id = id

    def __str__(self):
        return str(self.id)


class TwosComplement(Expr):
    def __init__(self, expr):
        self.expr = expr





