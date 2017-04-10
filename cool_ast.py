from scope import *
from cool_types import *
from typing import List
import cool_global as GLOBAL
from random import randint


class Node(object):
    """
    The base class for all ast, this class also define the top Scope
    and several helper function for all subclasses
    """
    topScope = Scope(enclosingClass=GLOBAL.topLevelClass, parent=None)

    def __init__(self):
        pass

    def error(self, msg):
        print(msg)
        GLOBAL.typecheckError = True

    def getType(self, scope: 'Scope', type_str: str) -> Type:
        """
        Given a type string: Int, String, Bool, SELF_TYPE, or class type
        return its type object, note that each type object is unique. pls
        see cool_global.py for more info
        """ 
        if type_str == 'Int':
            return GLOBAL.integerType
        elif type_str == 'String':
            return GLOBAL.stringType
        elif type_str == 'Bool':
            return GLOBAL.booleanType
        elif type_str == 'SELF_TYPE':
            return GLOBAL.selfType
        else:
            return scope.lookupType(type_str)

    def getInitByType(self, decType):
        """
        return a value base on the input type, this is used 
        to initialize different variable
        """
        if decType == GLOBAL.integerType:
            return 0
        elif decType == GLOBAL.stringType:
            return ""
        elif decType == GLOBAL.booleanType:
            return False
        else:
            return GLOBAL.void


class Program(Node):
    """
    program ::= [[class; ]]+
    """

    def __init__(self, classes: List['Class']):
        self.classes = classes

    def __str__(self):
        return "\n".join([str(c) for c in self.classes])

    def preprocess(self, scope):
        """
        Before we type check the program, we have to proprocess the whole
        program and record all the class declaration in order to support
        forward reference. 

        1. Walk through all class declaration header and record the class name,
           class type, class value(open a scope for method declarations)
        2. Walk through all class declartion again and record all inherited information
           (if there is one, or use object type as its inherited class type)
        3. For each class declaration, get its method declaration scope and start walking 
           through its all feature declarations. For each method declaration, a new scope
           will be created for its value information (please see scope.py for more info)
        """
        for c in self.classes:
            classType = ClassType(c.className)
            classScope = Scope(parent=scope)
            scope.add(c.className, classScope, classType)

        for c in self.classes:

            if c.inheritType:
                parentClassType = self.getType(scope, c.inheritType)
                if not parentClassType:
                    self.error("class {} is not defined".format(str(c.inheritType)))
                    
            else:
                parentClassType = GLOBAL.objectType

            classScope = scope.lookupLocal(c.className)
            classType = scope.lookupLocalType(c.className)
            classType.parent = parentClassType
            classScope.enclosingClass = classType
            classScope.inheritClassScope = scope.findScopeByType(
                self.topScope, parentClassType)

            for feature in c.features:
                if isinstance(feature, FeatureAttribute):
                    decClassType = self.getType(classScope, feature.decType)
                    classScope.add(feature.id, None, decClassType)
                else:
                    methodScope = Scope(parent=classScope)
                    methodScope.enclosingClass = classType
                    methodScope.inheritClassScope = classScope.inheritClassScope

                    formal_tys = [self.getType(
                        classScope, formal.decType) for formal in feature.formalParams]
                    ret_ty = self.getType(classScope, feature.retType)
                    methodType = FuncType(formal_tys, ret_ty)
                    classScope.add(feature.methodName, methodScope, methodType)

    def typecheck(self):
        topScope = Node.topScope
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
        """
        To type check a class:

        1. get the inherited class scope. We will need a list of method
           declarations from parent class.
        2. since the pass-in scope is the top-level scope, we have to first
           get the class scope(where we store method declaration) by class Name
        3. type check features using the class scope
        """

        if self.inheritType:
            inheritClassScope = topScope.getDefiningScope(self.inheritType)
        else:
            inheritClassScope = topScope.getDefiningScope('Object')

        newscope = topScope.getDefiningScope(self.className)

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
        """
        To type check a method declaration:

        1. lookup in scope and get the function type 
           (it is guarantee to exist as it has already been preprocessed)
        2. create a new scope for the method. 
        3. add all formal paramater and their types into the new scope
        4. type check the body of the method using the new scope
        5. check to see if the return type from step 4 is 'compatible' to 
           the declared type from the method header.

        There are a few things worth to be mentioned here:

        1. SELF_TYPE is not allowed to exist as a type of a formal paramter.
        2. the return type of method body (ty) and the declared return type of the method(decl_ty) 
           can be SELF_TYPE. 
        3. If ty is SELF_TYPE and decl_ty is not, then compare the enclosing class type 
           with decl_ty
        3. If ty is not SELF_TYPE but decl_ty is, then comparen the enclosing class type 
           with ty
        4. If both ty and decl_ty are SELF_TYPE, no action needed
        5. If both ty and decl_ty are NOT SELF_TYPE, then compare them and see if 
           ty is a subtype of decl_ty
        """

        functionType = scope.lookupType(self.methodName)
        formal_tys = functionType.param_tys
        ret_ty = functionType.ret_ty

        newscope = scope.lookup(self.methodName)
        for formal, formal_ty in zip(self.formalParams, formal_tys):
            if formal_ty is GLOBAL.selfType:
                self.error("SEFL_TYPE is not allowed to exist as a type of a formal paramter")
                return
            newscope.add(formal.id, None, formal_ty)

        _, ty = self.bodyExpr.typecheck(newscope)

        if ty == GLOBAL.selfType != ret_ty and not scope.enclosingClass.isSubclassOf(ret_ty) \
                or ty != GLOBAL.selfType == ret_ty and not ty.isSubclassOf(scope.enclosingClass) \
                or ty != GLOBAL.selfType != ret_ty and not ty.isSubclassOf(ret_ty):
            self.error("method declaration type mismatch\n {}".format(str(self)))
            

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
        """
        add the type declaration into scope and return the declared type
        """

        if self.id == "self":
            self.error("Illegal name: self cannot be an attribute name")
            return

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
    expr ::= ID <- expr
    """

    def __init__(self, id: str, expr: 'Expr'):
        self.id = id
        self.expr = expr

    def __str__(self):
        return "{} <- {}".format(str(self.id), str(self.expr))

    def typecheck(self, scope: Scope):
        """
        1. get the type of declared id 
        2. type check expression
        3. compare and see if the type of expression conforms the type of declared id
        """
        id_ty = scope.lookupType(self.id)

        if id_ty is GLOBAL.selfType:
            self.error("Illegal assignment: cannot assignment to SELF_TYPE")
            return

        _, e_ty = self.expr.typecheck(scope)

        if not e_ty.isSubclassOf(id_ty):
            self.error("Type mismatch for var {} and expression {}".format(
                str(id_ty), str(self.expr)))

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
        """
        There are two forms of dispatch:
            <id>(<expr>,...,<expr>)
            <expr>@<type>.id(<expr>,...,<expr>)

        We first need to find the correct method definition by:

        1. check if dispatchClassName exist. If so get the dispatch class 
           scope, else find the class scope of enclosing class 
        2. use the scope from step 1 and get the method definition
        3. type check method and see if formal parameters match arguments

        note that argument can be of type SELF_TYPE, if this is the case 
        then it should be converted to enclosingClassType
        """
        if isinstance(self.objExpr, Self):
            classType = scope.enclosingClass
        else:
            _, classType = self.objExpr.typecheck(scope)

        if not classType:
            self.error("error class {} not yet define".format(str(self.objExpr)))
            

        if self.dispatchedClassName:
            dispatchedClassType = self.getType(scope, self.dispatchedClassName)
            dispatchedClassScope = scope.findScopeByType(
                self.topScope, dispatchedClassType)
        else:
            dispatchedClassType = classType
            dispatchedClassScope = scope.findScopeByType(
                self.topScope, classType)

        if not classType.isSubclassOf(dispatchedClassType):
            self.error("Type mismatch, class {} is not a subclass of {}".format(
                str(classType.name), str(dispatchedClassType.name)))
            

        function_ty = dispatchedClassScope.lookupType(self.methodName)

        if not function_ty:
            self.error("dispatch method name {} is not defined".format(self.methodName))
            

        arg_tys = []
        for arg in self.arguments:
            _, arg_ty = arg.typecheck(scope)
            if arg_ty == GLOBAL.selfType:
                arg_ty = scope.enclosingClass
            arg_tys.append(arg_ty)

        for arg_ty, param_ty in zip(arg_tys, function_ty.param_tys):
            if not arg_ty.isSubclassOf(param_ty):
                self.error("type mismatch dispatch")
                

        if function_ty.ret_ty == GLOBAL.selfType:
            return None, classType

        return None, function_ty.ret_ty


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
            self.error("type mismatch if")
            

        _, thn_ty = self.thn.typecheck(scope)
        _, els_ty = self.els.typecheck(scope)

        if thn_ty == GLOBAL.selfType:
            thn_ty = scope.enclosingClass
        if els_ty == GLOBAL.selfType:
            els_ty = scope.enclosingClass

        mutual = thn_ty.mutualParentOfTwo(els_ty)

        if not mutual:
            self.error("if mismatch\n {}".format(str(self)))
            
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

        if cnd_ty is not GLOBAL.booleanType:
            self.error("error while loop type mismatch")
            
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
        s1 = "{} : {}".format(str(self.id), str(self.decType), str(self.init))
        s2 = " <- {}".format(str(self.init)) if self.init else ""
        return s1 + s2


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
        """
        for each let body, a new scope needs to be created. 
        """

        let_scope = Scope(parent=scope)
        let_scope.enclosingClass = scope.enclosingClass
        let_scope.inheritClassScope = scope.inheritClassScope
        scope.add('let' + str(randint(0, 10000)), let_scope, None)

        letVarDecls = []
        for decl in self.declareVars:
            decType = self.getType(scope, decl.decType)

            if decType is GLOBAL.selfType:
                self.error("Illegal binding: cannot bind SELF_TYPE in let expression")
                return

            if decl.init:
                decInitVal, decInitType = decl.init.typecheck(scope)
                if not decInitType.isSubclassOf(decType):
                    self.error("type mismatch at let declaration: init type {} is not a subclass of declared type {}".format(
                        str(decInitType.name), str(decType.name)))
                    
                letVarDecls.append((decl.id, decInitVal, decType))
            else:
                initVal = self.getInitByType(decType)
                letVarDecls.append((decl.id, initVal, decType))

            for id, val, ty in letVarDecls:
                let_scope.add(id, val, ty)

        return self.bodyExpr.typecheck(let_scope)


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

        action_ids_tys = []

        for action in self.actions:
            action_id_ty = self.getType(scope, action.defType)

            if action_id_ty is GLOBAL.selfType:
                self.error("Illegal type declaration: SELF_TYPE cannot be declared at here")
                return

            scope.add(action.id, None, action_id_ty)
            _, body_ty = action.body.typecheck(scope)
            scope.delete(action.id)

            action_ids_tys.append((action.id, body_ty))

        for action_id, action_ty in action_ids_tys:
            scope.add(action_id, None, action_ty)

        action_tys = [action_id_ty[1] for action_id_ty in action_ids_tys]

        ret_ty = Type.mutualParentOfAll(action_tys)

        if not ret_ty:
            self.error("error type mismatch")

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

        if ty1 is not GLOBAL.integerType and ty2 is not GLOBAL.integerType:
            self.error("type mismatch binaryop")
            
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

        if ty1 == GLOBAL.selfType:
            ty1 = scope.enclosingClass

        if ty2 == GLOBAL.selfType:
            ty2 = scope.enclosingClass

        prim_ty_set = {GLOBAL.integerType, GLOBAL.stringType, GLOBAL.booleanType} 

        if ty1 != ty2 and (ty1 in prim_ty_set or ty2 in prim_ty_set):
            self.error("type mismatch at = operator") 

        if not type(ty1) == type(ty2):
            self.error("type mismatch eq4")
            
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
        _, ty = self.expr.typecheck(scope)

        if ty is not GLOBAL.booleanType:
            self.error("boolena type mismatch")

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

    def __str__(self):
        return "~{}".format(str(self.expr))

    def typecheck(self, scope):
        _, ty = self.expr.typecheck(scope)

        if ty is not GLOBAL.integerType:
            self.error("neg type mismatch")
            
        return None, GLOBAL.integerType


if __name__ == "__main__":
    import sys
    import os
    import glob
    from parser import make_parser

    root_path = '/Users/Jack/Documents/programming/python/coolCompiler'
    test_folder = root_path + '/Tests'

    parser = make_parser()

    with open("Tests/bad2.cl") as file:
            cool_program_code = file.read()

    parse_result = parser.parse(cool_program_code)
    ret = parse_result.typecheck()
    if ret:
        self.error("successful")
