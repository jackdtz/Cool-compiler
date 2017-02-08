
class Node(object):
    def __init__(self):
        pass

class Program(Node):
    def __init__(self, classes):
        self.classes = classes

class Class(Node):
    def __init__(self, classType, features, inheritType):
        self.classType = classType
        self.inheritType = inheritType
        self.features = features

class Feature(Node):
    def __init__(self):
        pass

class FeatureMethod(Feature):
    def __init__(self, methodName, formalParams, retType, bodyExpr):
        self.methodName = methodName
        self.formalParams = formalParams
        self.retType = retType
        self.bodyExpr = bodyExpr

class FeatureAttribute(Feature):
    def __init__(self, id, decType, initExpr):
        self.id = id
        self.decType = decType
        self.initExpr = initExpr

class FormalParams(Node):
    def __init__(self, id, decType):
        self.id = id
        self.decType = decType

class Expr(Node):
    def __init__(self):
        pass

class AssignmentExpr(Expr):
    def __init__(self, id, expr):
        self.id = id
        self.expr = expr

class Dispatch(Expr):
    def __init__(self, objExpr, method, formalParams, parentClass=None):
        self.objExpr = objExpr
        self.method = method
        self.formalParams = formalParams
        self.parentClass = parentClass

class If(Expr):
    def __init__(self, condition, thenExpr, elseExpr):
        self.condition = condition
        self.thenExpr = thenExpr
        self.elseExpr = elseExpr

class While(Expr):
    def __init__(self, condition, bodyExpr):
        self.condition = condition
        self.bodyExpr = bodyExpr

class LetDecVar(Node):
    def __init__(self, id, decType, initVal=None):
        self.id = id
        self.decType = decType
        self.initVal = initVal


class Let(Expr):
    def __init__(self, declareVars, bodyExpr):
        self.declareVars = declareVars
        self.bodyExpr = bodyExpr


    


