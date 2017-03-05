
class Type(object):
    def __init__(self, val):
        self.val = val

class FuncType(Type): pass

class PrimFuncType(Type): pass

class IntType(Type): pass

class StringType(Type): pass

class BooleanType(Type): pass

class ClassType(Type):
    def __init__(self, parentType):
        self.parentType = parentType

