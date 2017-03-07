class Type(object):
    def __init__(self, parent : 'Type'=None):
        self.parent = parent

    def isSubclassOf(self, c):
        while self != None:
            if type(self) == type(c):
                return True
            self = self.parent
        return False


class Object(Type):
    pass


class FuncType(Type):
    def __init__(self, param_tys, ret_ty):
        super().__init__()
        self.param_tys = param_tys
        self.ret_ty = ret_ty


class PrimFuncType(Type):
    pass


class IntegerType(Type):
    pass


class StringType(Type):
    pass


class BooleanType(Type):
    pass


class SelfType(Type):
    pass


class ClassType(Type):
    def __init__(self, parentType):
        self.parentType = parentType

class TopLevelClass():
    pass
