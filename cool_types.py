from utils import *
from typing import List


class Type(object):
    def __init__(self, parent: 'Type'=None):
        self.parent = parent

    def isSubclassOf(self, c):
        while self != None:
            if type(self) == type(c):
                return True
            self = self.parent
        return False

    def lengthToRoot(self):
        count = 0
        s = self
        while s.parent != None:
            s = s.parent
            count += 1
        return count

    def mutualParentOfTwo(self, ty2):
        ty1 = self

        if not ty1 or not ty2:
            return None

        if ty1 == ty2 or type(ty1) == type(ty2):
            return ty1

        l1 = ty1.lengthToRoot()
        l2 = ty2.lengthToRoot()

        if l1 > l2:
            count = l1 - l2
            while count:
                ty1 = ty1.parent
                count -= 1
        elif l2 > l1:
            count = l2 - l1
            while count:
                ty2 = ty2.parent
                count -= 1

        while ty1 != ty2:
            ty1 = ty1.parent
            ty2 = ty2.parent

        if ty1 == ty2:
            return ty1

        return None

    @staticmethod        
    def mutualParentOfAll(tys: List['Type']):
        t = tys[0]
        for i in range(len(tys) - 1):
            t = t.mutualParentOfTwo(tys[i + 1])


class ObjectType(Type):
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
    pass



class TopLevelClass(ClassType):
    pass

class VoidType(Type):
    pass
