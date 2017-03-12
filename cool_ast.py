from scope import *
from cool_types import *
from utils import *
from typing import List
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

    def getType(self, scope:'Scope', type_str: str) -> Type:
        if type_str == 'Int':
            return GLOBAL.integerType
        elif type_str == 'String':
            return GLOBAL.stringType
        elif type_str == 'Bool':
            return GLOBAL.booleanType
        elif type_str == 'SELF_TYPE':
            return scope.enclosingClass
        else:
            return scope.lookupType(type_str)

    @staticmethod
    def fold_left_op(scope: Scope, c: 'Node'):
        return c.typecheck(scope)


class Program(Node):
    """
    program ::= [[class; ]]+
    """

    def __init__(self, classes: List['Class']):
        self.classes = classes

    def __str__(self):
        return "\n".join([str(c) for c in self.classes])

    def preprocess(self, scope):
        for c in self.classes:
            if c.inheritType:
                parentClassType = self.getType(scope, c.inheritType)
            else:
                parentClassType = GLOBAL.objectType

            classType = ClassType(parent=parentClassType)
            classScope = Scope(parent=scope)
            classScope.enclosingClass = classType 
            classScope.inheritClassScope = scope.findScopeByType(parentClassType)
            scope.add(c.className, classScope, classType)

            for feature in c.features:
                if isinstance(feature, FeatureAttribute):
                    decClassType = self.getType(classScope, feature.decType)
                    classScope.add(feature.id, None, decClassType)
                else:
                    methodScope = Scope(parent=classScope)
                    methodScope.enclosingClass = classType
                    methodScope.inheritClassScope = classScope.inheritClassScope

                    formal_tys = [self.getType(classScope, formal) for formal in feature.formalParams]
                    ret_ty = self.getType(classScope, feature.retType)
                    methodType = FuncType(formal_tys, ret_ty)
                    classScope.add(feature.methodName, methodScope, methodType)


    def typecheck(self):
        topScope = Scope(enclosingClass=GLOBAL.topLevelClass, parent=None)
        Scope.initTopScope(topScope)

        self.preprocess(topScope)

        for c in self.classes:
            c.typecheck(topScope)

        return topScope


class Class(Node):
    """
    class ::= class TYPE [inherits TYPE] { [feature;]* }
    """

    def __init__(self, className: str, features: List['Feature'], inheritType: str=None):
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

    def typecheck(self, topScope: Scope):

        if self.inheritType:
            inheritClassScope = topScope.getDefiningScope(self.inheritType)
        else:
            inheritClassScope = topScope.getDefiningScope('Object')

        newscope = topScope.getDefiningScope(self.className)
        newscope.inheritClassScope = inheritClassScope

        for feature in self.features:
            _, ty = feature.typecheck(newscope)

        return None, topScope.lookupLocalType(self.className)


class Feature(Node):
    def __init__(self):
        pass


class FeatureMethodDecl(Feature):
    """
    feature ::= ID(formals) : TYPE { expr }
    """

    def __init__(self, methodName: str, formalParams: List['FormalParam'], retType: str, bodyExpr: 'Expr'):
        self.methodName = methodName
        self.formalParams = formalParams
        self.retType = retType
        self.bodyExpr = bodyExpr

    def __str__(self):
        params = ", ".join([str(f) for f in self.formalParams])

        return "{}({}) : {} {{\n\t {} }};".format(str(self.methodName), params, str(self.retType), str(self.bodyExpr))

    def typecheck(self, scope: Scope):

        functionType = scope.lookupType(self.methodName)
        formal_tys = functionType.param_tys
        ret_ty = functionType.ret_ty

        newscope = scope.lookup(self.methodName)
        for formal, formal_ty in zip(self.formalParams, formal_tys):
            newscope.add(formal.id, None, formal_ty)

        _, ty = self.bodyExpr.typecheck(newscope)
        
        if isinstance(ty, SelfType):
            ty = scope.enclosingClass

        if not ty.isSubclassOf(ret_ty):
            print("method declaration type mismatch\n {}".format(str(self)))
            exit()

        return None, functionType


class FeatureAttribute(Feature):
    """
    feature ::= ID : TYPE [ <- expr ]
    """

    def __init__(self, id: str, decType: str, init: 'Expr'=None):
        self.id = id
        self.decType = decType
        self.init = init

    def __str__(self):
        if self.init:
            return "{} : {} <- {}".format(str(self.id), str(self.decType), str(self.init))
        else:
            return "{} : {}".format(str(self.id), str(self.decType))

    def typecheck(self, scope: Scope):
        decType = self.getType(scope, self.decType)
        scope.add(self.id, None, decType)
        return None, decType


class FormalParam(Node):
    """
    feature ::= ID : TYPE
    """

    def __init__(self, id: str, decType: str):
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

    def __init__(self, id: str, expr: 'Expr'):
        self.id = id
        self.expr = expr

    def __str__(self):
        return "{} <- {}".format(str(self.id), str(self.expr))

    def typecheck(self, scope: Scope):
        id_ty = scope.lookupType(self.id)

        _, e_ty = self.expr.typecheck(scope)

        if not e_ty.isSubclassOf(id_ty):
            print("Type mismatch for var {} and expression {}".format(
                str(id_ty), str(self.expr)))
            exit()

        return None, e_ty


class Dispatch(Expr):
    """
    expr ::= expr[@TYPE].ID( [ expr [[, expr]] ] )
    """

    def __init__(self, objExpr: 'Expr', method: str, arguments: List['Expr'], dispatchedClassName: str=None):
        self.objExpr = objExpr
        self.methodName = method
        self.arguments = arguments
        self.dispatchedClassName = dispatchedClassName

    def __str__(self):
        arguments = ", ".join([str(arg) for arg in self.arguments])

        if self.dispatchedClassName:
            return "{}@{}.{}({})".format(str(self.objExpr), str(self.dispatchedClassName), str(self.methodName), arguments)
        else:
            return "{}.{}({})".format(str(self.objExpr), str(self.methodName), arguments)

    def typecheck(self, scope: Scope):
        if isinstance(self.objExpr, Self):
            classType = scope.enclosingClass
        else:
            _, classType = self.objExpr.typecheck(scope)

        if not classType:
            print("error class {} not yet define".format(str(self.objExpr)))
            exit()

        if self.dispatchedClassName:
            dispatchedClassType = self.getType(scope, self.dispatchedClassName)
            dispatchedClassScope = scope.findScopeByType(dispatchedClassType)
        else:
            dispatchedClassType = classType
            dispatchedClassScope = scope.findScopeByType(classType)

        if not classType.isSubclassOf(dispatchedClassType):
            print("Type mismatch")
            exit()


        function_ty = dispatchedClassScope.lookupLocalType(self.methodName)

        if not function_ty:
            print("dispatch method name {} is not defined".format(self.methodName))
            exit()

        arg_tys = []
        for arg in self.arguments:
            _, arg_ty = arg.typecheck(scope)
            arg_tys.append(arg_ty)

        for arg_ty, param_ty in zip(arg_tys, function_ty.param_tys):
            if not arg_ty.isSubclassOf(param_ty):
                print("type mismatch dispatch")
                exit()

        if isinstance(function_ty.ret_ty,SelfType):
            return None, classType

        return None, function_ty.ret_ty


class MethodCall(Expr):
    """
    expr ::= ID( [ expr [, expr]* ] )
    """

    def __init__(self, id: str, args: List['Expr']):
        self.id = id
        self.args = args

    def __str__(self):
        # print(self.exprs)
        return "{}({})".format(str(self.id), ", ".join([str(e) for e in self.args]))

    def typecheck(self, scope):
        method_ty = scope.lookupType(self.id)

        if not method_ty:
            print("method {} is not defined".format(self.id))
            exit()


        if not isinstance(method_ty, FuncType):
            print("type mismatch method call 1")
            exit()

        arg_tys = []
        for arg in self.args:
            _, ty = arg.typecheck(scope)
            arg_tys.append(ty)

        for arg_ty, formal_ty in zip(arg_tys, method_ty.param_tys):
            if not arg_ty.isSubclassOf(formal_ty):
                print("type mismatch method call 2")
                exit()

        return None, method_ty.ret_ty


class If(Expr):
    """
    expr ::= if expr then expr else expr fi
    """

    def __init__(self, cnd: 'Expr', thn: 'Expr', els: 'Expr'):
        self.cnd = cnd
        self.thn = thn
        self.els = els

    def __str__(self):
        return "if {} then {} else {} fi".format(str(self.cnd), str(self.thn), str(self.els))

    def typecheck(self, scope):

        _, cnd_ty = self.cnd.typecheck(scope)

        if not isinstance(cnd_ty, BooleanType):
            print("type mismatch if")
            exit()

        _, thn_ty = self.thn.typecheck(scope)
        _, els_ty = self.els.typecheck(scope)

        mutual = thn_ty.mutualParentOfTwo(els_ty)

        if not mutual:
            print("if mismatch\n {}".format(str(self)))
            exit()

        return None, mutual


class While(Expr):
    """
    expr ::= while expr loop expr pool
    """

    def __init__(self, condition: 'Expr', bodyExpr: 'Expr'):
        self.condition = condition
        self.bodyExpr = bodyExpr

    def __str__(self):
        return "while {} loop {} pool".format(str(self.condition), str(self.bodyExpr))

    def typecheck(self, scope):
        _, cnd_ty = self.condition.typecheck(scope)

        if not isinstance(cnd_ty, BooleanType):
            print("error while loop type mismatch")
            exit()

        self.bodyExpr.typecheck(scope)

        return None, GLOBAL.objectType


class Block(Expr):
    """
    expr ::= { [expr; ]+ }
    """

    def __init__(self, exprs: List['Expr']):
        self.exprs = exprs

    def __str__(self):
        return "( {} )".format("\n".join([str(e) + ";" for e in self.exprs]))

    def typecheck(self, scope):

        for i in range(len(self.exprs) - 1):
            self.exprs[i].typecheck(scope)

        _, ty = self.exprs[-1].typecheck(scope)

        return None, ty


class LetVarDecl(Node):
    """
    expr ::= ID : TYPE <- expr
    """

    def __init__(self, id: str, decType: str, init: 'Expr'=None):
        self.id = id
        self.decType = decType
        self.init = init

    def __str__(self):
        return "{} : {} <- {}".format(str(self.id), str(self.decType), str(self.init))


class Let(Expr):
    """
    expr ::= let ID : TYPE [ <- expr ] [, ID : TYPE [ <- expr ]]* in expr
    """

    def __init__(self, declareVars: List['LetVarDecl'], bodyExpr: 'Expr'):
        self.declareVars = declareVars
        self.bodyExpr = bodyExpr

    def __str__(self):
        return "let {} \tin \t{}\n".format("\n".join(["\t" + str(decl) + "\n" for decl in self.declareVars]), str(self.bodyExpr))

    def typecheck(self, scope):

        letVarDecls = []

        for decl in self.declareVars:
            copiedScope = scope.copy()
            decType = self.getType(copiedScope, decl.decType)
            if decl.init:
                decInitVal, decInitType = decl.init.typecheck(copiedScope)
                if not decInitType.isSubclassOf(decType):
                    print("type mismatch at let declaration")
                    exit()
                scope.add(decl.id, decInitVal, decInitType)
            else:
                scope.add(decl.id, None, decType)

       
            
        return self.bodyExpr.typecheck(scope)

class CaseAction(Node):
    """
    action ::= ID : TYPE => expr
    """

    def __init__(self, id: str, defType: str, body: 'Expr'):
        self.id = id
        self.defType = defType
        self.body = body

    def __str__(self):
        return "{} : {} => {}".format(str(self.id), str(self.defType), str(self.body))


class Case(Expr):
    """
    expr ::= case expr of [ID : TYPE => expr; ]+ esac
    """

    def __init__(self, cond: 'Expr', actions: List['CaseAction']):
        self.cond = cond
        self.actions = actions

    def __str__(self):
        return (
            "case {} of\n"
            "{}"
            "esac"
        ).format(str(self.cond), ["\t" + str(action) + "\n" for action in self.actions])

    def typecheck(self, scope):
        _, cnd_ty = self.cond.typecheck(scope)

        action_tys = []

        for action in self.actions:
            copiedScope = scope.copy()
            action_id_ty = scope.getType(action.defType)
            copiedScope.add(action.id, None, action_id_ty)
            _, body_ty = action.body.typecheck(copiedScope)

            if not type(action_id_ty) == type(body_ty):
                print("case action type mismatch")
                exit()

            action_tys.append(body_ty)

        ret_ty = Type.mutualParentOfAll(action_tys)

        if not ret_ty:
            print("error type mismatch")

        return None, ret_ty


class NewConstruct(Expr):
    """
    expr ::= new Type
    """

    def __init__(self, objType: str):
        self.objType = objType

    def __str__(self):
        return "new " + str(self.objType)

    def typecheck(self, scope: Scope):
        if self.objType == 'self':
            return None, GLOBAL.selfType

        ty = scope.lookupType(self.objType)

        return None, ty


class IsVoid(Expr):
    """
    expr ::= isvoid expr
    """

    def __init__(self, expr: 'Expr'):
        self.expr = expr

    def __str__(self):
        return "isvoid " + str(self.expr)

    def typecheck(self, scope):
        val, ty = self.expr.typecheck(scope)

        return None, GLOBAL.booleanType


class BinaryOp(Expr):
    def __init__(self, e1: 'Expr', e2: 'Expr'):
        self.e1 = e1
        self.e2 = e2

    def typecheck(self, scope):
        _, ty1 = self.e1.typecheck(scope)
        _, ty2 = self.e2.typecheck(scope)

        if not isinstance(ty1, IntegerType) and not isinstance(ty2, IntegerType):
            print("type mismatch binaryop")
            exit()

        if isinstance(self, (Plus, Minus, Multiply, Divide)):
            return None, GLOBAL.integerType

        return None, GLOBAL.booleanType




class Plus(BinaryOp):
    """
    expr ::= expr + expr
    """

    def __init__(self, e1: 'Expr', e2: 'Expr'):
        super(Plus, self).__init__(e1, e2)

    def __str__(self):
        return str(self.e1) + " + " + str(self.e2)


class Minus(BinaryOp):
    """
    expr ::= expr - expr
    """

    def __init__(self, e1: 'Expr', e2: 'Expr'):
        super(Minus, self).__init__(e1, e2)

    def __str__(self):
        return str(self.e1) + " - " + str(self.e2)


class Multiply(BinaryOp):
    """
    expr ::= expr * expr
    """

    def __init__(self, e1: 'Expr', e2: 'Expr'):
        super(Multiply, self).__init__(e1, e2)

    def __str__(self):
        return str(self.e1) + " * " + str(self.e2)


class Divide(BinaryOp):
    """
    expr ::= expr / expr
    """

    def __init__(self, e1: 'Expr', e2: 'Expr'):
        super(Divide, self).__init__(e1, e2)

    def __str__(self):
        return str(self.e1) + " / " + str(self.e2)


class LessThan(BinaryOp):
    """
    expr ::= expr < expr
    """

    def __init__(self, e1: 'Expr', e2: 'Expr'):
        super(LessThan, self).__init__(e1, e2)

    def __str__(self):
        return str(self.e1) + " < " + str(self.e2)


class LessEq(BinaryOp):
    """
    expr ::= expr <= expr
    """

    def __init__(self, e1: 'Expr', e2: 'Expr'):
        super(LessEq, self).__init__(e1, e2)

    def __str__(self):
        return str(self.e1) + " <= " + str(self.e2)


class Eq(BinaryOp):
    """
    expr ::= expr = expr
    """

    def __init__(self, e1: 'Expr', e2: 'Expr'):
        super(Eq, self).__init__(e1, e2)

    def __str__(self):
        return str(self.e1) + " = " + str(self.e2)

    def typecheck(self, scope):
        _, ty1 = self.e1.typecheck(scope)
        _, ty2 = self.e2.typecheck(scope)

        if isinstance(ty1, IntegerType) and not isinstance(ty2, IntegerType) \
           or not isinstance(ty1, IntegerType) and isinstance(ty2, IntegerType):
            print("type mismatch Eq1")
            exit()

        if isinstance(ty1, BooleanType) and not isinstance(ty2, BooleanType) \
           or not isinstance(ty1, BooleanType) and isinstance(ty2, BooleanType):
            print("type mismatch Eq2")
            exit()

        if isinstance(ty1, StringType) and not isinstance(ty2, StringType) \
           or not isinstance(ty1, StringType) and isinstance(ty2, StringType):
            print("type mismatch Eq3")
            exit()

        if not type(ty1) == type(ty2):
            print("type mismatch eq4")
            exit()

        return None, GLOBAL.booleanType


class GreaterThan(BinaryOp):
    """
    expr ::= expr > expr
    """

    def __init__(self, e1: 'Expr', e2: 'Expr'):
        super(GreaterThan, self).__init__(e1, e2)

    def __str__(self):
        return str(self.e1) + " > " + str(self.e2)


class GreaterEq(BinaryOp):
    """
    expr ::= expr >= expr
    """

    def __init__(self, e1: 'Expr', e2: 'Expr'):
        super(GreaterEq, self).__init__(e1, e2)

    def __str__(self):
        return str(self.e1) + " >= " + str(self.e2)


class Not(Expr):
    """
    expr ::= not expr
    """

    def __init__(self, expr: 'Expr'):
        self.expr = expr

    def __str__(self):
        return "not" + str(self.expr)

    def typecheck(self, scope):
        _, ty = expr.typecheck(scope)

        if not isinstance(ty, BooleanType):
            print("boolena type mismatch")

        return None, GLOBAL.booleanType


class Integer(Expr):
    """
    expr ::= integer
    """

    def __init__(self, ival: int):
        self.ival = ival

    def __str__(self):
        return str(self.ival)

    def typecheck(self, scope: Scope):
        return self.ival, GLOBAL.integerType


class String(Expr):
    """
    expr ::= string
    """

    def __init__(self, sval: str):
        self.sval = sval

    def __str__(self):
        return str(self.sval)

    def typecheck(self, scope):
        return self.sval, GLOBAL.stringType


class Boolean(Expr):
    """
    expr ::= boolean
    """

    def __init__(self, bval: bool):
        self.bval = bval

    def __str__(self):
        return str(self.bval)

    def typecheck(self, scope):
        return self.bval, GLOBAL.booleanType


class Self(Expr):
    """
    expr ::= self
    """

    def __init__(self):
        pass

    def __str__(self):
        return "self"

    def typecheck(self, scope):
        return None, GLOBAL.selfType


class Id(Expr):
    """
    expr ::= ID
    """

    def __init__(self, id: str):
        self.id = id

    def __str__(self):
        return str(self.id)

    def typecheck(self, scope: Scope):
        print(self.id)

        ty = scope.lookupType(self.id)

        return None, ty


class ParenExpr(Expr):
    """
    expr ::= (expr)
    """

    def __init__(self, e: 'Expr'):
        self.e = e

    def __str__(self):
        return "({})".format(str(self.e))

    def typecheck(self, scope: Scope):
        return self.e.typecheck(scope)


class Neg(Expr):
    def __init__(self, expr):
        self.expr = expr

    def typecheck(self, scope):
        _, ty = self.expr.typecheck(scope)

        if not isinstance(ty, IntegerType):
            print("neg type mismatch")
            exit()

        return None, GLOBAL.integerType



if __name__ == "__main__":
    import sys, os, glob
    from parser import make_parser

    root_path = '/Users/Jack/Documents/programming/python/coolCompiler'
    test_folder = root_path + '/Tests'       

    parser = make_parser() 


    with open("Tests/arith.cl") as file:
            cool_program_code = file.read()

    parse_result = parser.parse(cool_program_code)
    print(parse_result.typecheck())