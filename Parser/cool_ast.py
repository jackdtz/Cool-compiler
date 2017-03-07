from scope import *
from cool_types import *
from utils import *
from typing import *
import cool_global as GLOBAL
class Node(object):

    ops = [
        "+", "-", "*", "/", 
        "~", "=",
        "<", "<=",
        ">", ">="
    ]
    def __init__(self):
        pass

    def getType(self, scope : 'Scope', type_str : str) -> Type:
        if type_str == 'Int':
            return IntegerType
        elif type_str == 'String':
            return StringType
        elif type_str == 'Boolean':
            return BooleanType
        elif type_str == 'self':
            return SelfType
        else:
            return scope.tlookup(type_str)


    @staticmethod
    def fold_left_op(scope : Scope, c : 'Node'):
        return c.typecheck(scope)

class Program(Node):
    """
    program ::= [[class; ]]+
    """
    def __init__(self, classes : List['Class']):
        self.classes = classes

    def __str__(self):
        return "\n".join([str(c) for c in self.classes])

    def typecheck(self):
        topLevelClass = TopLevelClass()
        topScope = Scope(selfclass=topLevelClass, parent=None)

        finalScope, ty = fold_left(self.fold_left_op, topScope, self.classes)

        return finalScope

     

class Class(Node):
    """
    class ::= class TYPE [inherits TYPE] { [feature;]* }
    """
    def __init__(self, className : str, features : List['Feature'], inheritType : str=None):
        self.className = className
        self.inheritType = inheritType
        self.features = features

    def __str__(self):
        if self.features != None:
            features = ";\n ".join([str(f) for f in self.features])
        else:
            features = ""  

        if self.inheritType:
            return "class {} inherits {} {{ {} }};".format(str(self.className), str(self.inheritType), features)
        else:
            return "class {} {{\n {} \n}};".format(str(self.className), features)

    def typecheck(self, scope : Scope):

        if self.inheritType:
            parentType = self.getType(scope, self.inheritType)
        else:
            parentType = GLOBAL.ObjectType

        copiedScope = scope.copy()
        classType = ClassType(self.parentType)
        copiedScope.tadd(self.className, classType)
        newscope = Scope.openScope(parent=copiedScope, selfclass=ClassType(self.className))
        finalScope, ty = fold_left(self.fold_left_op, newscope, self.features)

        return finalScope, ty

class Feature(Node):
    def __init__(self):
        pass

class FeatureMethodDecl(Feature):
    """
    feature ::= ID( [ formal [, formal]* ] ) : TYPE { expr }
    """
    def __init__(self, methodName : str, formalParams : List['FormalParam'], retType : str, bodyExpr : 'Expr'):
        self.methodName = methodName
        self.formalParams = formalParams
        self.retType = retType
        self.bodyExpr = bodyExpr

    def __str__(self):
        if len(self.formalParams) == 1 and self.formalParams[0] == None:
            params = ""     
        else:
            params = ", ".join([str(f) for f in self.formalParams])

        return "{}({}) : {} {{\n\t {} }};".format(str(self.methodName), params , str(self.retType), str(self.bodyExpr))

    def typecheck(self, scope : Scope):
        copiedScope = scope.copy()

        formal_tys = [self.getType(scope, formal.decType) for formal in self.formalParams]
        ret_ty = self.getType(scope, ret_ty)
        functionType = functionType(formal_tys, ret_ty)
        copiedScope.tadd(self.methodName, functionType)
        
        newscope = Scope.openscope(parent=copiedScope)

        finalScope, ty = fold_left(self.fold_left_op, newscope, self.bodyExprs)

        return finalScope, None

class FeatureAttribute(Feature):
    """
    feature ::= ID : TYPE [ <- expr ]
    """
    def __init__(self, id : str, decType : str, init : 'Expr'=None):
        self.id = id
        self.decType = decType
        self.init = init

    def __str__(self):
        if self.init:
            return "{} : {} <- {}".format(str(self.id), str(self.decType), str(self.init))
        else:
            return "{} : {}".format(str(self.id), str(self.decType))
        
    def typecheck(self, scope : Scope):
        decType = self.getType(scope, self.decType)
        scope.tadd(self.id, decType)
        return scope, None
        

class FormalParam(Node):
    """
    feature ::= ID : TYPE
    """
    def __init__(self, id : str, decType : str):
        self.id = id
        self.decType = decType

    def __str__(self):
        return "{} : {}".format(str(self.id), str(self.decType))


class Expr(Node):
    def __init__(self):
        pass

class AssignmentExpr(Expr):
    """
    expr ::= ID<- expr
    """
    def __init__(self, id : str, expr : 'Expr'):
        self.id = id
        self.expr = expr

    def __str__(self):
        return "{} <- {}".format(str(self.id), str(self.expr))

    def typecheck(self, scope : Scope):
        id_ty = Scope.vlookup(scope, self.id)
        
        newscope, e_ty = self.expr.typecheck(scope)

        if not e_ty.isSubClassOf(id_ty):
            print("Type mismatch for var {} and expression {}".format(str(id_ty), str(self.expr)))
            exit()

        return scope, e_ty

class Dispatch(Expr):
    """
    expr ::= expr[@TYPE].ID( [ expr [[, expr]] ] )
    """
    def __init__(self, objExpr : 'Expr', method : str, arguments : List['Expr'], parent : str=None):
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

    def typecheck(self, scope : Scope):
        if isinstance(self.objExpr, Self):
            t0 = scope.selfclass
        else:
            scope, t0 = self.objExpr.typecheck(scope)

        if self.parent:
            tt = self.getType(scope, self.parent)
        else:
            tt = t0

        


        # if self.objExpr == 'self':
        #     t0 = scope.selfclass
        # else:
        #     scope, t0 = self.objExpr.typecheck(scope)

        # if self.parent:
        #     tt = scope.lookup(self.parent)
        #     if not t0.isSubClassOf(tt):
        #         print("Type mismatch here")
        #         exit()
        # else:
        #     tt = t0

        # function_ty = scope.lookup(tt)
        # arg_tys = [scope.lookup(arg) for arg in self.arguments]

        # if not len(function_ty.param_tys) == len(arg_tys):
        #     print("length mismatch")
        #     exit()

        # for arg_ty, param_ty in zip(arg_tys, function_ty.param_tys):
        #     if not arg_ty.isSubClassOf(param_ty):
        #         print("type mismatched")
        #         exit()

        # # final_ty = 
                


class MethodCall(Expr):
    """
    expr ::= ID( [ expr [, expr]* ] )
    """
    def __init__(self, id : str, exprs : List['Expr']):
        self.id = id
        self.exprs = exprs

    def __str__(self):
        # print(self.exprs)
        return "{}({})".format(str(self.id), ", ".join([str(e) for e in self.exprs]))

class If(Expr):
    """
    expr ::= if expr then expr else expr fi
    """
    def __init__(self, cnd : 'Expr', thn : 'Expr', els : 'Expr'):
        self.cnd = cnd
        self.thn = thn
        self.els = els

    def __str__(self):
        return "if {} then {} else {} fi".format(str(self.cnd), str(self.thn), str(self.els))

class While(Expr):
    """
    expr ::= while expr loop expr pool
    """
    def __init__(self, condition : 'Expr', bodyExpr : 'Expr'):
        self.condition = condition
        self.bodyExpr = bodyExpr

    def __str__(self):
        return "while {} loop {} pool".format(str(self.condition), str(self.bodyExpr))

class Block(Expr):
    """
    expr ::= { [expr; ]+ }
    """
    def __init__(self, exprs : List['Expr']):
        self.exprs = exprs

    def __str__(self):
        return "( {} )".format("\n".join([str(e) + ";" for e in self.exprs]))

class LetVarDecl(Node):
    """
    expr ::= ID : TYPE <- expr
    """
    def __init__(self, id : str, decType : str, init : 'Expr'=None):
        self.id = id
        self.decType = decType
        self.init = init

    def __str__(self):
        return "{} : {} <- {}".format(str(self.id), str(self.decType), str(self.init))

class Let(Expr):
    """
    expr ::= let ID : TYPE [ <- expr ] [, ID : TYPE [ <- expr ]]* in expr
    """
    def __init__(self, declareVars : List['LetVarDecl'], bodyExpr : 'Expr'):
        self.declareVars = declareVars
        self.bodyExpr = bodyExpr

    def __str__(self):
        return "let {} \tin \t{}\n".format("\n".join(["\t" + str(decl) + "\n" for decl in self.declareVars]), str(self.bodyExpr))
        

class CaseAction(Node):
    """
    action ::= ID : TYPE => expr
    """
    def __init__(self, id : str, defType : str, body : 'Expr'):
        self.id = id
        self.defType = defType
        self.body = body

    def __str__(self):
        return "{} : {} => {}".format(str(self.id), str(self.defType), str(self.body))

class Case(Expr):
    """
    expr ::= case expr of [ID : TYPE => expr; ]+ esac
    """
    def __init__(self, cond : 'Expr', actions : List['CaseAction']):
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
    def __init__(self, objType : str):
        self.objType = objType

    def __str__(self):
        return "new " + str(self.objType)

    def typecheck(self, scope : Scope):
        if self.objType == 'self':
            return scope, SelfType
        
        ty = scope.lookup(self.objType)

        return scope, ty

        
        

class IsVoid(Expr):
    """
    expr ::= isvoid expr
    """
    def __init__(self, expr : 'Expr'):
        self.expr = expr

    def __str__(self):
        return "isvoid " + str(self.expr)

class BinaryOp(Expr):
    def __init__(self, e1 : 'Expr', e2 : 'Expr'):
        self.e1 = e1
        self.e2 = e2

class Plus(BinaryOp):
    """
    expr ::= expr + expr
    """
    def __init__(self, e1 : 'Expr', e2 : 'Expr'):
        super(Plus, self).__init__(e1, e2)

    def __str__(self):
        return str(self.e1) + " + " + str(self.e2)

class Minus(BinaryOp):
    """
    expr ::= expr - expr
    """
    def __init__(self, e1 : 'Expr', e2 : 'Expr'):
        super(Minus, self).__init__(e1, e2)

    def __str__(self):
        return str(self.e1) + " - " + str(self.e2)

class Multiply(BinaryOp):
    """
    expr ::= expr * expr
    """
    def __init__(self, e1 : 'Expr', e2 : 'Expr'):
        super(Multiply, self).__init__(e1, e2)

    def __str__(self):
        return str(self.e1) + " * " + str(self.e2)

class Divide(BinaryOp):
    """
    expr ::= expr / expr
    """
    def __init__(self, e1 : 'Expr', e2 : 'Expr'):
        super(Divide, self).__init__(e1, e2)

    def __str__(self):
        return str(self.e1) + " / " + str(self.e2)

class LessThan(BinaryOp):
    """
    expr ::= expr < expr
    """
    def __init__(self, e1 : 'Expr', e2 : 'Expr'):
        super(LessThan, self).__init__(e1, e2)

    def __str__(self):
        return str(self.e1) + " < " + str(self.e2)

class LessEq(BinaryOp):
    """
    expr ::= expr <= expr
    """
    def __init__(self, e1 : 'Expr', e2 : 'Expr'):
        super(LessEq, self).__init__(e1, e2)

    def __str__(self):
        return str(self.e1) + " <= " + str(self.e2)

class Eq(BinaryOp):
    """
    expr ::= expr = expr
    """
    def __init__(self, e1 : 'Expr', e2 : 'Expr'):
        super(Eq, self).__init__(e1, e2)

    def __str__(self):
        return str(self.e1) + " = " + str(self.e2)

class GreaterThan(BinaryOp):
    """
    expr ::= expr > expr
    """
    def __init__(self, e1 : 'Expr', e2 : 'Expr'):
        super(GreaterThan, self).__init__(e1, e2)
    
    def __str__(self):
        return str(self.e1) + " > " + str(self.e2)

class GreaterEq(BinaryOp):
    """
    expr ::= expr >= expr
    """
    def __init__(self, e1 : 'Expr', e2 : 'Expr'):
        super(GreaterEq, self).__init__(e1, e2)

    def __str__(self):
        return str(self.e1) + " >= " + str(self.e2)

class Not(Expr):
    """
    expr ::= not expr
    """
    def __init__(self, expr : 'Expr'):
        self.expr = expr

    def __str__(self):
        return "not" + str(self.expr)

class Integer(Expr):
    """
    expr ::= integer
    """
    def __init__(self, ival : int):
        self.ival = ival

    def __str__(self):
        return str(self.ival)


    def typecheck(self, scope : Scope):
        return scope, IntegerType(self)
    

class String(Expr):
    """
    expr ::= string
    """
    def __init__(self, sval : str):
        self.sval = sval
    
    def __str__(self):
        return str(self.sval)

    def typecheck(self, scope):
        return scope, StringType(self)

class Boolean(Expr):
    """
    expr ::= boolean
    """
    def __init__(self, bval : bool):
        self.bval = bval

    def __str__(self):
        return str(self.bval)

    def typecheck(self, scope):
        return scope, BooleanType(self)

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
    def __init__(self, id : str):
        self.id = id

    def __str__(self):
        return str(self.id)

    def typecheck(self, scope : Scope):
        
        ty = scope.look(self.id)

        return scope, ty

class ParenExpr(Expr):
    """
    expr ::= (expr)
    """
    def __init__(self, e : 'Expr'):
        self.e = e
    
    def __str__(self):
        return "({})".format(str(self.e))

    def typecheck(self, scope : Scope):
        return self.e.typecheck(scope)


class TwosComplement(Expr):
    def __init__(self, expr):
        self.expr = expr





